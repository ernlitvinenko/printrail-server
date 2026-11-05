import secrets
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Annotated, Any

import bcrypt
import jwt
from fastapi import Header

from core.environment import Config
from core.helpers.dtime import get_current_dt

ALGORITHM = "HS256"


@dataclass
class TokenData:
    sub: int
    type: str
    exp: datetime
    iat: datetime


def create_access_token(sub: int, expires_delta_seconds: int | None = None) -> str:
    """Create a signed JWT access token for the given account id."""
    if expires_delta_seconds is None:
        expires_delta_seconds = Config.JWT_TOKEN_LIFETIME_MINUTES * 60
    now = get_current_dt()
    payload = {
        "sub": str(sub),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=expires_delta_seconds),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT. Raises jwt.InvalidTokenError subclasses on failure."""
    return jwt.decode(token, Config.SECRET_KEY, algorithms=[ALGORITHM])


@dataclass
class NewPasswordData:
    password: str
    hash: str


def generate_new_password() -> NewPasswordData:
    alphabet = string.ascii_letters + string.digits
    pwd = "".join(secrets.choice(alphabet) for _ in range(12))
    return NewPasswordData(password=pwd, hash=generate_password_hash(pwd))


def generate_password_hash(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash.encode())


async def get_current_user(token: Annotated[str, Header()]):
    return None
