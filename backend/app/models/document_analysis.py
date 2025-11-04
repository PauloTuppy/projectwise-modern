import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .base import Base

class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    # AI Analysis Results
    summary = Column(Text)  # 3-sentence summary
    extracted_data = Column(Text)  # Key data extracted
    ocr_text = Column(Text)  # Full OCR text
    key_entities = Column(JSON)  # {persons, companies, dates, etc}
    
    # Quality Metrics
    confidence_score = Column(Float)  # 0-1 confidence
    processing_time = Column(Float)  # seconds
    
    # Traceability
    analyzed_by = Column(String(100))  # AI model version
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", backref="analysis")
