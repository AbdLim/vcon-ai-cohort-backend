from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ParticipantBase(BaseModel):
    user_id: int
    cohort_id: int
    role: str = "student"
    metadata_json: Optional[Dict[str, Any]] = None

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantUpdate(BaseModel):
    role: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class ParticipantMetricsUpdate(BaseModel):
    sessions_attended: Optional[int] = None
    average_talk_time_pct: Optional[float] = None
    health_score: Optional[float] = None

class ParticipantResponse(ParticipantBase):
    id: int
    sessions_attended: int
    average_talk_time_pct: float
    health_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
