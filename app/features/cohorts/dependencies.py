from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.features.cohorts.service import CohortService

async def get_cohort_service(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> CohortService:
    return CohortService(session)
