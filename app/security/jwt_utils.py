from jose import jwt,JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
           payload,
           settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )



def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        )
        return payload

    except JWTError:
        raise HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        )
