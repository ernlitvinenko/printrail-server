from fastapi import APIRouter

from core.models.requests.auth import LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
async def login(login_data: LoginRequest):
    pass


@router.post("/logout")
async def logout():
    pass


@router.post("/token/refresh")
async def token_rotation():
    pass


@router.get("/me")
async def get_current_user():
    pass
