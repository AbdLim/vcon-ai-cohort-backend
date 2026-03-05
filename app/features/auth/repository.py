from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.features.auth.models import Auth

class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Auth | None:
        stmt = select(Auth).options(selectinload(Auth.profile)).where(Auth.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, auth_id: int) -> Auth | None:
        stmt = select(Auth).options(selectinload(Auth.profile)).where(Auth.id == auth_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
