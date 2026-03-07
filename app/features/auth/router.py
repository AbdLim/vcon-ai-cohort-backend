from fastapi import APIRouter, Depends, status, Body
from typing import Annotated
from app.features.auth.schemas import UserCreate, Token, UserResponse, UserLogin
from app.features.auth.service import AuthService
from app.features.auth.dependencies import (
    get_auth_service,
    get_current_user,
    require_permission,
)
from app.features.auth.models import Auth
from app.core.responses import APIResponse, SuccessResponse, ErrorResponse

router = APIRouter()


@router.post("/signup", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate, service: Annotated[AuthService, Depends(get_auth_service)]
):
    user = await service.register_user(user_in)
    return SuccessResponse.create("User registered successfully", data=user)


@router.post("/login", response_model=APIResponse[Token])
async def login(
    user_in: UserLogin, service: Annotated[AuthService, Depends(get_auth_service)]
):
    token = await service.authenticate_user(user_in)
    return SuccessResponse.create("Login successful", data=token)


@router.post("/refresh", response_model=APIResponse[Token])
async def refresh_token(
    refresh_token: Annotated[str, Body(embed=True)],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    token = await service.refresh_token(refresh_token)
    return SuccessResponse.create("Token refreshed successfully", data=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: Annotated[str, Body(embed=True)],
    service: Annotated[AuthService, Depends(get_auth_service)],
    current_user: Annotated[Auth, Depends(get_current_user)],
):
    await service.logout(refresh_token)


@router.get("/admin-only", response_model=APIResponse[dict])
async def admin_only(
    current_user: Annotated[Auth, Depends(require_permission("admin:access"))],
):
    return SuccessResponse.create(
        "Admin access granted", data={"role": current_user.role}
    )
