import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.infrastructure.redis import redis_client
from unittest.mock import MagicMock
# Import models to register them with Base
from app.features.auth.models import Auth
from app.features.users.models import User
from app.features.cohorts.models import Organization, Cohort
from app.features.participants.models import Participant
from app.features.sessions.models import Session

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=None,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

@pytest.fixture(scope="session", autouse=True)
async def shutdown_resources():
    yield
    await redis_client.close()
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass # Session is handled by fixture

    app.dependency_overrides[get_db] = override_get_db
    
    # Mock Redis
    # We can either mock the wrapper or the redis instance.
    # It's easier to mock the methods on redis_client for simple tests.
    # However, if we want to test token revocation, having a dict-based mock is better.
    
    mock_redis = MagicMock()
    mock_store = {}
    
    async def get(key: str):
        return mock_store.get(key)
    
    async def set(key: str, value: str, expire: int = None):
        mock_store[key] = value
        
    async def delete(key: str):
        if key in mock_store:
            del mock_store[key]
            
    # Monkeypatch the redis_client instance methods
    redis_client.get = get
    redis_client.set = set
    redis_client.delete = delete
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
        
    app.dependency_overrides.clear()
