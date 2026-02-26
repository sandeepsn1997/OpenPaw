from typing import Optional
import json
import os
import requests
from ...db import SessionLocal
from .whatsapp_manager import wa_manager

# ---------------------------------------------------------------------------
# WhatsApp Multi-Provider Implementation
# ---------------------------------------------------------------------------

def _get_config():
    """Retrieve WhatsApp configuration from database."""
    from .backend import WhatsAppConfigDB
    db = SessionLocal()
    try:
        row = db.query(WhatsAppConfigDB).filter(WhatsAppConfigDB.user_id == "default").first()
        if row:
            return {
                "provider_type": row.provider_type,
                "config": json.loads(row.config_json)
            }
        return None
    finally:
        db.close()


def _send_callmebot(config: dict, to: str, message: str) -> str:
    """Send message via CallMeBot (Forever Free for personal use)."""
    apikey = config.get("cmb_apikey")
    if not apikey:
        return "Error: CallMeBot API Key is not configured."
    
    # CallMeBot usually sends to the number that registered the key.
    # We use the 'to' parameter if it matches, otherwise it just goes to the registered phone.
    url = "https://api.callmebot.com/whatsapp.php"
    params = {
        "phone": to, # CallMeBot expects the phone number here
        "text": message,
        "apikey": apikey
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            return json.dumps({"success": True, "message": "CallMeBot accepted the message.", "to": to})
        return f"CallMeBot Error: {res.text}"
    except Exception as e:
        return f"Request to CallMeBot failed: {str(e)}"


def _send_meta(config: dict, to: str, message: str, media_url: Optional[str] = None) -> str:
    """Send message via Official Meta Cloud API (Permanent free tier)."""
    token = config.get("meta_access_token")
    phone_id = config.get("meta_phone_id")
    
    if not token or not phone_id:
        return "Error: Meta Access Token and Phone Number ID are required."

    url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Construct payload
    clean_to = to.replace("+", "").replace(" ", "")
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_to
    }

    if media_url:
        # Simplistic implementation for media (assumes image for now)
        payload["type"] = "image"
        payload["image"] = {"link": media_url}
        if message:
            payload["image"]["caption"] = message
    else:
        payload["type"] = "text"
        payload["text"] = {"body": message}

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        data = res.json()
        if res.status_code == 200:
            return json.dumps({"success": True, "sid": data.get("messages", [{}])[0].get("id"), "to": to})
        return f"Meta API Error: {json.dumps(data)}"
    except Exception as e:
        return f"Request to Meta API failed: {str(e)}"


def _send_twilio(config: dict, to: str, message: str, media_url: Optional[str] = None) -> str:
    """Send message via Twilio."""
    account_sid = config.get("account_sid")
    auth_token = config.get("auth_token")
    from_number = config.get("from_number", "+14155238886")

    if not account_sid or not auth_token:
        return "Error: Twilio credentials not configured."

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        kwargs = {
            "from_": f"whatsapp:{from_number}",
            "to": f"whatsapp:{to}",
        }
        if media_url:
            kwargs["media_url"] = [media_url]
            if message:
                kwargs["body"] = message
        else:
            kwargs["body"] = message

        msg = client.messages.create(**kwargs)
        return json.dumps({"success": True, "sid": msg.sid, "status": msg.status, "to": to})
    except Exception as e:
        return f"Twilio Error: {str(e)}"


# ---------------------------------------------------------------------------
# Skill entry point
# ---------------------------------------------------------------------------
async def run(
    action: str,
    to: Optional[str] = None,
    message: Optional[str] = None,
    media_url: Optional[str] = None,
    message_sid: Optional[str] = None,
) -> str:
    """Execute WhatsApp actions via configured provider."""

    full_config = _get_config()
    if not full_config and action != "get_config":
        return "WhatsApp is not configured. Go to Settings and choose a provider (CallMeBot for Forever Free personal use)."

    provider = full_config["provider_type"] if full_config else "none"
    config = full_config["config"] if full_config else {}

    if action == "get_config":
        return json.dumps({
            "configured": bool(full_config),
            "provider": provider,
            "can_send_media": provider in ["twilio", "meta_official"]
        })

    if action in ["send_message", "send_media"]:
        if not to:
            return "Error: 'to' recipient number is required."
        if not message and not media_url:
            return "Error: either 'message' or 'media_url' is required."

        if provider == "wa_web":
            import os
            import asyncio
            session_db = os.path.join(os.path.dirname(__file__), "session.db")
            if wa_manager.status != "connected" and os.path.exists(session_db):
                print(f"[WA] AI agent detected disconnected state, starting client...")
                wa_manager.start_client()
                for _ in range(15):
                    if wa_manager.status == "connected":
                        break
                    await asyncio.sleep(1)
            
            success = wa_manager.send_message(to, message or media_url)
            if success:
                return json.dumps({"success": True, "to": to, "message": "Message sent via linked WhatsApp Web account."})
            return "Error: WhatsApp Web is not linked or not connected. Please link your account in Settings."
        elif provider == "callmebot":
            if media_url:
                return "CallMeBot (Free) only supports text messages. Use Twilio or Meta for media."
            return _send_callmebot(config, to, message)
        
        elif provider == "meta_official":
            return _send_meta(config, to, message, media_url)
        
        elif provider == "twilio":
            return _send_twilio(config, to, message, media_url)

    return f"Action '{action}' is not supported yet for provider '{provider}'."
