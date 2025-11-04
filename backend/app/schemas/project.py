from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid
from .user import UserResponse

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    disciplines: Optional[List[str]] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    disciplines: Optional[List[str]] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: str
    disciplines: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role: str
    user: UserResponse
    
    class Config:
        from_attributes = True