from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.cohorts.models import Cohort
from app.features.sessions.models import Session

class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_overview(self) -> dict:
        # Count active cohorts (for now, simply all cohorts)
        cohorts_count_stmt = select(func.count()).select_from(Cohort)
        cohorts_count_result = await self.session.execute(cohorts_count_stmt)
        active_cohorts = cohorts_count_result.scalar() or 0

        # Get the latest processed sessions
        latest_sessions_stmt = (
            select(Session)
            .where(Session.status == "completed")
            .order_by(Session.created_at.desc())
            .limit(5)
        )
        latest_sessions_result = await self.session.execute(latest_sessions_stmt)
        latest_sessions = latest_sessions_result.scalars().all()

        return {
            "active_cohorts": active_cohorts,
            "latest_sessions": latest_sessions
        }
