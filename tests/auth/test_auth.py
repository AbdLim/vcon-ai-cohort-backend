import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    response = await client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": "newuser@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["email"] == "newuser@example.com"
    assert data["data"]["profile"]["full_name"] == "Test User"
    assert "id" in data["data"]
    assert "password" not in data["data"]

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # Setup
    await client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": "login@example.com", "password": "password123"}
    )
    
    # Login
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    # Setup
    await client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": "refresh@example.com", "password": "password123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "refresh@example.com", "password": "password123"}
    )
    refresh_token = login_res.json()["data"]["refresh_token"]
    
    # Refresh
    response = await client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["refresh_token"] != refresh_token # Should be rotated

@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    # Setup
    await client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": "logout@example.com", "password": "password123"}
    )
    login_res = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "logout@example.com", "password": "password123"}
    )
    tokens = login_res.json()["data"]
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Logout
    response = await client.post(
        f"{settings.API_V1_STR}/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 204
    
    # Verify refresh token is invalid (we mocked redis, so we trust logic calls it)
    # Ideally we check the mock_store in a unit test, but this is an integration test.
    # We can try to refresh again to verify it fails
    
    fail_res = await client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert fail_res.status_code == 401
