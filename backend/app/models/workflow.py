from sqlalchemy import Column, String, UUID, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from .base import Base

class RFIStatusEnum(str, enum.Enum):
    OPEN = "open"
    ANSWERED = "answered"
    CLOSED = "closed"

class TransmittalStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"

class RFI(Base):
    __tablename__ = "rfis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    status = Column(String(50), default=RFIStatusEnum.OPEN)
    priority = Column(String(50), default="medium")
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transmittal(Base):
    __tablename__ = "transmittals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_ids = Column(JSON, default=list)
    status = Column(String(50), default=TransmittalStatusEnum.DRAFT)
    approval_chain = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    approvers = Column(JSON, default=list)
    auto_notify = Column(JSON, default=True)
    requires_all_approval = Column(JSON, default=True)