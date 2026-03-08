from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.features.sessions.schemas import SessionResponse

class CohortBase(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: int

class CohortCreate(CohortBase):
    pass

class CohortUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    organization_id: Optional[int] = None

class CohortResponse(CohortBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CohortWithSessionsResponse(CohortResponse):
    sessions: List[SessionResponse] = []
