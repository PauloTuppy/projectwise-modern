import uuid
import os
from fastapi import UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import boto3

from app.models.document import Document, DocumentVersion, DocumentStatusEnum, FileTypeEnum
from app.config import settings

class DocumentService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    async def upload_document(
        self,
        db: Session,
        project_id: str,
        file: UploadFile,
        user_id: str,
        name: str = None,
        description: str = None,
        discipline: str = None
    ) -> Document:
        """Upload a new document or new version"""
        
        # Determine file type
        file_ext = file.filename.split(".")[-1].lower()
        file_type = self._get_file_type(file_ext)
        
        # Upload to S3
        s3_key = f"projects/{project_id}/documents/{uuid.uuid4()}"
        file_content = await file.read()
        
        self.s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type
        )
        
        s3_url = f"s3://{settings.AWS_S3_BUCKET}/{s3_key}"
        
        # Create document record
        document = Document(
            id=uuid.uuid4(),
            project_id=uuid.UUID(project_id),
            name=name or file.filename,
            description=description,
            file_type=file_type,
            discipline=discipline,
            owner_id=uuid.UUID(user_id),
            status=DocumentStatusEnum.DRAFT
        )
        
        # Create first version
        version = DocumentVersion(
            id=uuid.uuid4(),
            document_id=document.id,
            version_number=1,
            file_path=s3_url,
            file_size=len(file_content),
            uploader_id=uuid.UUID(user_id),
            change_summary="Initial upload"
        )
        
        document.current_version_id = version.id
        document.versions.append(version)
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    def get_document(self, db: Session, document_id: str) -> Document:
        """Get document by ID"""
        return db.query(Document).filter(
            Document.id == uuid.UUID(document_id),
            Document.deleted_at == None
        ).first()
    
    def list_project_documents(
        self,
        db: Session,
        project_id: str,
        skip: int = 0,
        limit: int = 10,
        discipline: str = None,
        status: str = None
    ) -> list:
        """List documents in project with optional filters"""
        query = db.query(Document).filter(
            Document.project_id == uuid.UUID(project_id),
            Document.deleted_at == None
        )
        
        if discipline:
            query = query.filter(Document.discipline == discipline)
        
        if status:
            query = query.filter(Document.status == status)
        
        return query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
    
    def get_document_versions(self, db: Session, document_id: str) -> list:
        """Get all versions of a document"""
        return db.query(DocumentVersion).filter(
            DocumentVersion.document_id == uuid.UUID(document_id)
        ).order_by(desc(DocumentVersion.version_number)).all()
    
    def restore_version(self, db: Session, document_id: str, version_id: str) -> Document:
        """Restore document to a previous version"""
        document = self.get_document(db, document_id)
        version = db.query(DocumentVersion).filter(
            DocumentVersion.id == uuid.UUID(version_id),
            DocumentVersion.document_id == uuid.UUID(document_id)
        ).first()
        
        if not version:
            raise ValueError("Version not found")
        
        # Create a new version based on the old one
        new_version = DocumentVersion(
            id=uuid.uuid4(),
            document_id=document.id,
            version_number=len(document.versions) + 1,
            file_path=version.file_path,
            file_size=version.file_size,
            change_summary=f"Restored from version {version.version_number}"
        )
        
        document.versions.append(new_version)
        document.current_version_id = new_version.id
        document.updated_at = datetime.utcnow()
        
        db.add(new_version)
        db.commit()
        
        return document
    
    def delete_document(self, db: Session, document_id: str):
        """Soft delete a document"""
        document = self.get_document(db, document_id)
        if document:
            document.deleted_at = datetime.utcnow()
            db.commit()
    
    def _get_file_type(self, extension: str) -> str:
        """Determine file type from extension"""
        extension_map = {
            "pdf": FileTypeEnum.PDF,
            "dwg": FileTypeEnum.DWG,
            "docx": FileTypeEnum.DOCX,
            "xlsx": FileTypeEnum.XLSX,
            "txt": FileTypeEnum.TXT,
            "jpg": FileTypeEnum.IMAGE,
            "png": FileTypeEnum.IMAGE,
            "gif": FileTypeEnum.IMAGE,
        }
        return extension_map.get(extension, FileTypeEnum.PDF)