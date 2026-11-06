from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from core.depends.session import Storages
from core.helpers.auth import decode_token
from core.models.database.account import Account


async def _get_current_user(
    storages: Storages, Authorization: Annotated[str | None, Header()] = None
) -> Account:

    if Authorization is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Authorization header missing"
        )
    token_parts = Authorization.split(" ")
    if len(token_parts) != 2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Incorrect authorization header format",
        )

    token_type, token = token_parts
    if token_type != "Bearer":
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Token type incorrect format"
        )
    try:
        token_data = decode_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Invalud token: {exc}"
        )

    account = await storages.account_storage.get(token_data.sub)

    if account is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    return account


User = Annotated[Account, Depends(_get_current_user)]
