import secrets
import string
from dataclasses import dataclass
from typing import Annotated

import bcrypt
from fastapi import Header

# @dataclass
# class TokenData:
#     sub: int
#     token_type: Literal[]
#     exp: datetime
#     iat: datetime
#     jti: int | None = None
#
# async def generate_access_token(user: Account):
#     token_payload = TokenData(sub=user.id, exp=get_current_dt() + timedelta(minutes=Config.JWT_TOKEN_LIFETIME_MINUTES), iat=get_current_dt())
#
#     # TODO change uuid and write it into database.
#     refresh_token_payload = TokenData(sub=user.id, exp=get_current_dt() + timedelta(minutes=Config.JWT_TOKEN_LIFETIME_MINUTES), iat=get_current_dt())
#     access_token = jwt.encode({key: val for key, val in asdict(token_payload).items() if val is not None}, key=Config.SECRET_KEY, algorithm="HS256")
#
# # DEPENDS
#
#


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
