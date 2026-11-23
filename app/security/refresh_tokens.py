import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken
import uuid

REFRESH_TOKEN_EXPIRE_DAYS = 7

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def store_refresh_token(
        db: Session,
        user_id: int,
        token: str,
        family_id: uuid.UUID,
        ) -> RefreshToken:
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
        )


    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(token),
        expires_at=expires_at,
        family_id=family_id,
        )

    db.add(refresh_token)
    db.flush()

    return refresh_token

