from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UploadResponse(BaseModel):
    task_id: str
    status: str

class SessionBase(BaseModel):
    title: str
    cohort_id: int

class SessionCreate(SessionBase):
    pass

class UrlUploadRequest(SessionBase):
    url: str

class SessionResponse(SessionBase):
    id: int
    vcon_url: Optional[str] = None
    transcription_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
