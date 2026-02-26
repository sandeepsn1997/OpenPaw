"""WhatsApp skill backend: Multi-provider configuration management."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import Session

from ...database import Base, WhatsAppConfigDB
from ...db import get_db

route_prefix = "/skills/whatsapp"
router = APIRouter()

import io
import base64
import os
import segno
from .whatsapp_manager import wa_manager

class WhatsAppConfigureRequest(BaseModel):
    # This matches whatever fields the frontend sends based on SkillSettings values
    provider_type: str
    cmb_apikey: Optional[str] = None
    meta_access_token: Optional[str] = None
    meta_phone_id: Optional[str] = None
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None
    from_number: Optional[str] = None


import os

class WhatsAppService:
    def __init__(self, db: Session, user_id: str = "default"):
        self.db = db
        self.user_id = user_id

    def configure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        provider_type = data.get("provider_type", "twilio")
        
        row = self.db.query(WhatsAppConfigDB).filter(WhatsAppConfigDB.user_id == self.user_id).first()
        if not row:
            row = WhatsAppConfigDB(user_id=self.user_id)
            self.db.add(row)
        
        row.provider_type = provider_type
        # In a real app, we'd encrypt sensitive fields here
        row.config_json = json.dumps(data)
        row.updated_at = datetime.utcnow()
        
        self.db.commit()
        return {"success": True, "message": f"WhatsApp configured successfully using {provider_type}"}

    def status(self) -> Dict[str, Any]:
        row = self.db.query(WhatsAppConfigDB).filter(WhatsAppConfigDB.user_id == self.user_id).first()
        if not row:
            return {"connected": False}
        
        config = json.loads(row.config_json)
        is_connected = True
        
        if row.provider_type == "wa_web":
            # Auto-start client if session exists but it's disconnected
            session_db = os.path.join(os.path.dirname(__file__), "session.db")
            if wa_manager.status == "disconnected" and os.path.exists(session_db):
                wa_manager.start_client()
            is_connected = (wa_manager.status == "connected")

        # Return merged dict for frontend to prepopulate fields
        return {
            "connected": is_connected,
            "provider_type": row.provider_type,
            **config
        }

    def revoke(self) -> Dict[str, Any]:
        # Stop the background client
        wa_manager.stop_client()
        
        # Delete the session database file to ensure a clean slate
        session_db = os.path.join(os.path.dirname(__file__), "session.db")
        if os.path.exists(session_db):
            try:
                os.remove(session_db)
                print(f"[WA] Session database deleted.")
            except Exception as e:
                print(f"[WA] Error deleting session database: {e}")

        # Remove the database record
        row = self.db.query(WhatsAppConfigDB).filter(WhatsAppConfigDB.user_id == self.user_id).first()
        if row:
            self.db.delete(row)
            self.db.commit()
        return {"revoked": True}


@router.get("/status")
def whatsapp_status(db: Session = Depends(get_db)):
    return WhatsAppService(db).status()


@router.post("/configure")
def whatsapp_configure(payload: Dict[str, Any], db: Session = Depends(get_db)):
    # Use Dict[str, Any] because fields are dynamic
    return WhatsAppService(db).configure(payload)


@router.post("/revoke")
def whatsapp_revoke(db: Session = Depends(get_db)):
    return WhatsAppService(db).revoke()

# --- WhatsApp Web Linking Endpoints ---

@router.post("/link/start")
def whatsapp_link_start():
    wa_manager.start_client()
    return {"status": "starting"}

@router.get("/link/status")
def whatsapp_link_status():
    return {
        "status": wa_manager.status,
        "is_connected": wa_manager.status == "connected"
    }

@router.get("/link/qr")
def whatsapp_link_qr():
    if not wa_manager.qr_code:
        raise HTTPException(status_code=404, detail="QR code not ready")
    
    # Generate PNG from QR string
    qr = segno.make(wa_manager.qr_code)
    buff = io.BytesIO()
    qr.save(buff, kind='png', scale=8)
    base64_qr = base64.b64encode(buff.getvalue()).decode('utf-8')
    
    return {"qr": f"data:image/png;base64,{base64_qr}"}
