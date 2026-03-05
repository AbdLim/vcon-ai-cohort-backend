from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
import bcrypt
from app.core.config import settings

ALGORITHM = settings.ALGORITHM

def create_access_token(subject: Union[str, Any]) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

import uuid

def create_refresh_token() -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt requires bytes
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), 
        hashed_password.encode("utf-8")
    )

def get_password_hash(password: str) -> str:
    # bcrypt.hashpw returns bytes, we decode to string for storage
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")
