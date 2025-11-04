import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from .base import Base

class ProjectStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    disciplines = Column(JSON, default=list)  # ["Architecture", "Structure", "MEP"]
    status = Column(String(50), default=ProjectStatusEnum.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    owner = relationship("User", foreign_keys=[owner_id])

class ProjectMember(Base):
    __tablename__ = "project_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="viewer")  # owner, manager, editor, viewer
    permissions = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User")