from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class DocumentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    discipline: Optional[str] = None

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    discipline: Optional[str] = None
    status: Optional[str] = None

class DocumentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    file_type: str
    discipline: Optional[str]
    status: str
    current_version_id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentVersionResponse(BaseModel):
    id: uuid.UUID
    version_number: int
    file_path: str
    file_size: int
    uploader_id: uuid.UUID
    change_summary: str
    created_at: datetime

    class Config:
        from_attributes = True
