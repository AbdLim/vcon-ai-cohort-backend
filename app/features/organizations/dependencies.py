from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.features.organizations.service import OrganizationService

async def get_organization_service(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> OrganizationService:
    return OrganizationService(session)
