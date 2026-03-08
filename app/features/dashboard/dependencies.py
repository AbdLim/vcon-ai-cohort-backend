from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.db.session import get_db
from app.features.dashboard.service import DashboardService

async def get_dashboard_service(session: Annotated[AsyncSession, Depends(get_db)]) -> DashboardService:
    return DashboardService(session)

