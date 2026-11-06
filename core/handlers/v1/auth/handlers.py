from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from core.depends.auth import User
from core.depends.session import Storages
from core.environment import Config
from core.helpers.auth import check_password, create_access_token, decode_token
from core.models.database.dto.models import AccountDTO
from core.models.requests.auth import LoginRequest, RotationRequest
from core.models.responses.auth import LoginResponse
from core.storage.session_storage_type import set_session_username

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
async def login(login_data: LoginRequest, storages: Storages) -> LoginResponse:

    account = await storages.account_storage.find_by_login(login_data.login)

    if account is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid login or password"
        )

    if not check_password(login_data.password.get_secret_value(), account.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid login or password"
        )

    set_session_username(storages, str(account.login))

    token = create_access_token(
        account.id, expires_delta_seconds=Config.JWT_TOKEN_LIFETIME_MINUTES * 60
    )
    refresh_token = create_access_token(
        account.id,
        expires_delta_seconds=Config.JWT_REFRESH_LIFETIME_DAYS * 60 * 60 * 24,
    )

    await storages.account_storage.rotate_refresh_tokens(account.id, refresh_token)

    return LoginResponse(access_token=token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(user: User, storages: Storages):
    await storages.account_storage.drop_refresh_token(account_id=user.id)
    return JSONResponse({"status": "ok"})


@router.post("/token/refresh")
async def token_rotation(
    rotation_request: RotationRequest, storages: Storages
) -> LoginResponse:

    token_data = decode_token(rotation_request.refresh_token)
    account = await storages.account_storage.get(token_data.sub)

    if account is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not founded")

    refresh_token_instance = await storages.account_storage.get_refresh_token(
        account_id=account.id
    )

    if refresh_token_instance is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Incorrect rotation token"
        )
    if refresh_token_instance.refresh_token != rotation_request.refresh_token:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Incorrect rotation token"
        )

    token = create_access_token(
        account.id, expires_delta_seconds=Config.JWT_TOKEN_LIFETIME_MINUTES * 60
    )
    refresh_token = create_access_token(
        account.id,
        expires_delta_seconds=Config.JWT_REFRESH_LIFETIME_DAYS * 60 * 60 * 24,
    )
    await storages.account_storage.rotate_refresh_tokens(account.id, refresh_token)

    return LoginResponse(access_token=token, refresh_token=refresh_token)


@router.get("/me")
async def get_current_user(user: User, storages: Storages):
    # Смотрим есть ли Refresh token в базе, если нет - значит пользователь вышел или не залогинился
    if not await storages.account_storage.is_refresh_token_exists(user.id):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User logged out")

    await storages.session.refresh(user, attribute_names=["employee"])
    await storages.session.refresh(
        user.employee, attribute_names=["position", "contacts"]
    )

    return AccountDTO.model_validate(user)
