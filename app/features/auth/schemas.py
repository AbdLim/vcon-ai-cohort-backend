from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserProfile(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserResponse(UserBase):
    id: int
    profile: Optional[UserProfile] = None
    model_config = ConfigDict(from_attributes=True)
