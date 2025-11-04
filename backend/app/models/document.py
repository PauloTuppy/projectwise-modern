import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime, Integer, ForeignKey, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from .base import Base

class DocumentStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"

class FileTypeEnum(str, enum.Enum):
    PDF = "pdf"
    DWG = "dwg"
    DOCX = "docx"
    XLSX = "xlsx"
    TXT = "txt"
    IMAGE = "image"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    file_type = Column(String(50), default=FileTypeEnum.PDF)
    discipline = Column(String(100))
    status = Column(String(50), default=DocumentStatusEnum.DRAFT)
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="document", cascade="all, delete-orphan")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)  # S3 URL
    file_size = Column(Integer)  # in bytes
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    change_summary = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="versions")