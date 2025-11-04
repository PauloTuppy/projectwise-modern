from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class RFICreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class RFIUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class RFIResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    priority: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class TransmittalCreate(BaseModel):
    document_ids: List[uuid.UUID]
    approval_chain: Optional[List[dict]] = None

class TransmittalUpdate(BaseModel):
    status: Optional[str] = None
    approval_chain: Optional[List[dict]] = None

class TransmittalResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
