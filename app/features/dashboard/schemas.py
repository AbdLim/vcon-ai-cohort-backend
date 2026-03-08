from pydantic import BaseModel, ConfigDict
from typing import List
from app.features.sessions.schemas import SessionResponse

class DashboardOverviewResponse(BaseModel):
    active_cohorts: int
    latest_sessions: List[SessionResponse]

    model_config = ConfigDict(from_attributes=True)
