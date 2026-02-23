"""Email skill backend: Gmail OAuth + inbox/send/reply APIs."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException, Query
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import Session

from ...config import settings
from ...database import Base
from ...db import get_db

route_prefix = "/skills/email"
router = APIRouter()

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


class GmailCredentialDB(Base):
    __tablename__ = "skill_email_gmail_credentials"
    __table_args__ = {"extend_existing": True}

    user_id = Column(String, primary_key=True, default="default")
    email = Column(String, nullable=True)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=True)
    token_uri = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    scopes = Column(Text, nullable=False)
    expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str


class ReplyEmailRequest(BaseModel):
    body: str = Field(..., min_length=1)


class GmailService:
    def __init__(self, db: Session, user_id: str = "default"):
        self.db = db
        self.user_id = user_id
        self._cipher = Fernet(self._derive_fernet_key(settings.oauth_token_encryption_key))

    @staticmethod
    def _derive_fernet_key(secret: str) -> bytes:
        raw = (secret or "").encode("utf-8")
        if len(raw) < 32:
            raw = raw.ljust(32, b"0")
        return base64.urlsafe_b64encode(raw[:32])

    def _ensure_server_configured(self) -> None:
        if not settings.gmail_client_id or not settings.gmail_client_secret:
            raise HTTPException(status_code=503, detail="Gmail integration is not configured on the server.")

    def _flow(self, state: Optional[str] = None) -> Flow:
        config = {
            "web": {
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        return Flow.from_client_config(config, scopes=GMAIL_SCOPES, state=state, redirect_uri=settings.gmail_redirect_uri)

    def connect_url(self) -> Dict[str, str]:
        self._ensure_server_configured()
        flow = self._flow()
        auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
        return {"auth_url": auth_url, "state": state}

    def _encrypt(self, value: Optional[str]) -> Optional[str]:
        return self._cipher.encrypt(value.encode("utf-8")).decode("utf-8") if value else None

    def _decrypt(self, value: Optional[str]) -> Optional[str]:
        return self._cipher.decrypt(value.encode("utf-8")).decode("utf-8") if value else None

    def save_callback_token(self, code: str, state: Optional[str]) -> Dict[str, Any]:
        self._ensure_server_configured()
        flow = self._flow(state=state)
        flow.fetch_token(code=code)
        creds = flow.credentials
        profile = build("gmail", "v1", credentials=creds).users().getProfile(userId="me").execute()

        row = self.db.query(GmailCredentialDB).filter(GmailCredentialDB.user_id == self.user_id).first()
        if not row:
            row = GmailCredentialDB(user_id=self.user_id)
            self.db.add(row)

        row.email = profile.get("emailAddress")
        row.encrypted_access_token = self._encrypt(creds.token) or ""
        row.encrypted_refresh_token = self._encrypt(creds.refresh_token)
        row.token_uri = creds.token_uri or "https://oauth2.googleapis.com/token"
        row.client_id = creds.client_id or settings.gmail_client_id
        row.scopes = json.dumps(creds.scopes or GMAIL_SCOPES)
        row.expiry = creds.expiry
        row.updated_at = datetime.utcnow()
        self.db.commit()
        return {"connected": True, "email": row.email}

    def _credentials(self) -> Credentials:
        row = self.db.query(GmailCredentialDB).filter(GmailCredentialDB.user_id == self.user_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Gmail account not connected.")

        creds = Credentials(
            token=self._decrypt(row.encrypted_access_token),
            refresh_token=self._decrypt(row.encrypted_refresh_token),
            token_uri=row.token_uri,
            client_id=row.client_id,
            client_secret=settings.gmail_client_secret,
            scopes=json.loads(row.scopes),
        )
        creds.expiry = row.expiry.replace(tzinfo=timezone.utc) if row.expiry else None
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            row.encrypted_access_token = self._encrypt(creds.token) or row.encrypted_access_token
            row.expiry = creds.expiry
            row.updated_at = datetime.utcnow()
            self.db.commit()
        return creds

    def _api(self):
        return build("gmail", "v1", credentials=self._credentials())

    def status(self) -> Dict[str, Any]:
        row = self.db.query(GmailCredentialDB).filter(GmailCredentialDB.user_id == self.user_id).first()
        return {"connected": bool(row), "email": row.email if row else None}

    def revoke(self) -> Dict[str, Any]:
        row = self.db.query(GmailCredentialDB).filter(GmailCredentialDB.user_id == self.user_id).first()
        if row:
            self.db.delete(row)
            self.db.commit()
        return {"revoked": True}

    def list_messages(self, unread_only: bool = False, max_results: int = 20) -> List[Dict[str, Any]]:
        api = self._api()
        payload = api.users().messages().list(
            userId="me", labelIds=["INBOX"], q="is:unread" if unread_only else None, maxResults=max_results
        ).execute()
        out = []
        for item in payload.get("messages", []):
            msg = api.users().messages().get(userId="me", id=item["id"], format="metadata").execute()
            headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
            out.append({"id": msg["id"], "threadId": msg.get("threadId"), "snippet": msg.get("snippet"), "from": headers.get("from"), "subject": headers.get("subject")})
        return out

    def get_message(self, message_id: str) -> Dict[str, Any]:
        api = self._api()
        msg = api.users().messages().get(userId="me", id=message_id, format="full").execute()
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        return {"id": msg["id"], "threadId": msg.get("threadId"), "snippet": msg.get("snippet"), "from": headers.get("from"), "to": headers.get("to"), "subject": headers.get("subject"), "payload": msg.get("payload")}

    def send_email(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        api = self._api()
        raw_email = f"To: {to}\r\nSubject: {subject}\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n{body}"
        encoded = base64.urlsafe_b64encode(raw_email.encode("utf-8")).decode("utf-8")
        req: Dict[str, Any] = {"raw": encoded}
        if thread_id:
            req["threadId"] = thread_id
        sent = api.users().messages().send(userId="me", body=req).execute()
        return {"id": sent.get("id"), "threadId": sent.get("threadId")}

    def reply_email(self, message_id: str, body: str) -> Dict[str, Any]:
        original = self.get_message(message_id)
        subject = original.get("subject") or ""
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"
        return self.send_email(to=original.get("from"), subject=subject, body=body, thread_id=original.get("threadId"))


@router.get("/connect")
def gmail_connect(db: Session = Depends(get_db)):
    return GmailService(db).connect_url()


@router.get("/callback")
def gmail_callback(code: str = Query(...), state: Optional[str] = Query(None), db: Session = Depends(get_db)):
    return GmailService(db).save_callback_token(code, state)


@router.get("/status")
def gmail_status(db: Session = Depends(get_db)):
    return GmailService(db).status()


@router.post("/revoke")
def gmail_revoke(db: Session = Depends(get_db)):
    return GmailService(db).revoke()


@router.get("/inbox")
def gmail_inbox(unread_only: bool = Query(False), max_results: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return GmailService(db).list_messages(unread_only=unread_only, max_results=max_results)


@router.get("/messages/{message_id}")
def gmail_get_message(message_id: str, db: Session = Depends(get_db)):
    return GmailService(db).get_message(message_id)


@router.post("/send")
def gmail_send(payload: SendEmailRequest, db: Session = Depends(get_db)):
    return GmailService(db).send_email(payload.to, payload.subject, payload.body)


@router.post("/messages/{message_id}/reply")
def gmail_reply(message_id: str, payload: ReplyEmailRequest, db: Session = Depends(get_db)):
    return GmailService(db).reply_email(message_id, payload.body)
