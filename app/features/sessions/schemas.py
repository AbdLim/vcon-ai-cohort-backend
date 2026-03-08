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

from pydantic import Field

class SessionResponse(SessionBase):
    id: int
    vcon_url: Optional[str] = Field(default=None, validation_alias="vcon_file_url")
    transcription_url: Optional[str] = Field(default=None, validation_alias="audio_file_url")
    status: str
    summary: Optional[str] = None
    topics_json: Optional[list] = None
    action_items_json: Optional[list] = None
    questions_asked_json: Optional[list] = None
    talk_listen_ratios_json: Optional[dict] = None
    key_moments_json: Optional[list] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
