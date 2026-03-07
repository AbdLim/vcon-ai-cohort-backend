import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.features.auth.models import Auth

@pytest.mark.asyncio
async def test_rbac_admin_access(client: AsyncClient, db_session: AsyncSession):
    # 1. Create admin user
    email = "admin@example.com"
    password = "password123"
    
    await client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": email, "password": password}
    )
    
    # Manually promote to admin (Auth model holds the role)
    stmt = update(Auth).where(Auth.email == email).values(role="admin")
    await db_session.execute(stmt)
    await db_session.commit()
    
    # Login
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": password}
    )
    token = login_res.json()["data"]["access_token"]
    
    # Access admin endpoint
    response = await client.get(
        f"{settings.API_V1_STR}/auth/admin-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["role"] == "admin"

@pytest.mark.asyncio
async def test_rbac_user_access_denied(client: AsyncClient):
    # 1. Create normal user
    email = "user@example.com"
    password = "password123"
    
    await client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": email, "password": password}
    )
    
    # Login
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": password}
    )
    token = login_res.json()["data"]["access_token"]
    
    # Access admin endpoint
    response = await client.get(
        f"{settings.API_V1_STR}/auth/admin-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json()["message"] == "Not enough permissions"
