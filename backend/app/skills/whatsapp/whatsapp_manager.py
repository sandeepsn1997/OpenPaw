import os
import threading
import time
from typing import Optional
from neonize.client import NewClient
from neonize.events import (
    ConnectedEv,
    MessageEv,
    QREv,
    PairStatusEv,
)
from neonize.utils import log
from ...db import SessionLocal
from ...database import WhatsAppConfigDB
import json
from datetime import datetime

class WhatsAppManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.client: Optional[NewClient] = None
        self.qr_code: Optional[str] = None
        self.status: str = "disconnected" # disconnected, connecting, qr_ready, connected
        self.db_path = os.path.join(os.path.dirname(__file__), "session.db")

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _register_events(self):
        if not self.client:
            return

        @self.client.event(QREv)
        def on_qr(client: NewClient, qr: QREv):
            print(f"[WA] QR Object received: {type(qr)}")
            # QREv from neonize (protobuf) has a 'Codes' field which is a list.
            if hasattr(qr, "Codes") and qr.Codes:
                self.qr_code = qr.Codes[0]
                print(f"[WA] Extracted QR Code from Codes[0] (Length: {len(self.qr_code)})")
            else:
                # Fallback or diagnostic logging
                self.qr_code = str(qr)
                print(f"[WA] Fallback: QR Code as string (Length: {len(self.qr_code)})")
                print(f"[WA] QR Fields: {dir(qr)}")
            
            self.status = "qr_ready"

        @self.client.event(ConnectedEv)
        def on_connected(client: NewClient, ev: ConnectedEv):
            self.status = "connected"
            self.qr_code = None
            print(f"[WA] Connected!")
            
            # Persist the configuration as 'wa_web' automatically so the skill is usable
            db = SessionLocal()
            try:
                row = db.query(WhatsAppConfigDB).filter(WhatsAppConfigDB.user_id == "default").first()
                if not row:
                    row = WhatsAppConfigDB(user_id="default")
                    db.add(row)
                
                row.provider_type = "wa_web"
                # Store empty config or existing if any
                if not row.config_json:
                    row.config_json = json.dumps({"provider_type": "wa_web"})
                
                row.updated_at = datetime.utcnow()
                db.commit()
                print(f"[WA] Persisted 'wa_web' provider to database.")
            except Exception as e:
                print(f"[WA] Failed to persist config: {e}")
            finally:
                db.close()

        @self.client.event(PairStatusEv)
        def on_pair_status(client: NewClient, ev: PairStatusEv):
            print(f"[WA] Pair Status: {ev}")

    def start_client(self):
        if self.client and self.status == "connected":
            return

        def _run():
            try:
                # Initialize client
                self.client = NewClient(self.db_path)
                
                # Register events
                self._register_events()
                
                self.status = "connecting"
                print(f"[WA] Starting client...")
                self.client.connect()
            except Exception as e:
                print(f"[WA] Client Error: {e}")
                self.status = "error"

        # Run in background thread
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def stop_client(self):
        if self.client:
            # Note: neonize might not have a clean 'stop' yet depending on version, 
            # but we can at least nullify our reference.
            self.status = "disconnected"
            self.client = None
            self.qr_code = None

    def send_message(self, to: str, message: str) -> bool:
        if not self.client or self.status != "connected":
            return False
        
        try:
            import re
            from neonize.utils import build_jid
            
            # Remove all non-digits to get the clean phone number
            clean_number = re.sub(r'\D', '', to)
            
            print(f"[WA] Sending to: {clean_number}")
            
            # neonize requires a JID object, not a string
            jid = build_jid(clean_number, "s.whatsapp.net")
            
            self.client.send_message(jid, message)
            
            print(f"[WA] Successfully sent message to {clean_number}")
            return True
        except Exception as e:
            print(f"[WA] Send Error: {e}")
            return False

wa_manager = WhatsAppManager.get_instance()
