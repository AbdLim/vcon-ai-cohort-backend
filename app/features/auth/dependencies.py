from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.features.auth.service import AuthService
from app.features.auth.repository import AuthRepository
from app.core.config import settings
from app.features.auth.models import Auth
from app.core.rbac import rbac

http_bearer = HTTPBearer(description="JWT Bearer token")


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(session))


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Auth:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        auth_id: str | None = payload.get("sub")
        if auth_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    auth = await service.repository.get_by_id(int(auth_id))

    if auth is None:
        raise credentials_exception
    return auth


def require_permission(permission: str):
    """
    Dependency to enforce RBAC permissions.
    Usage: @Depends(require_permission("resource:action"))
    """

    async def dependency(auth: Auth = Depends(get_current_user)):
        if not rbac.has_permission(auth.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return auth

    return dependency
