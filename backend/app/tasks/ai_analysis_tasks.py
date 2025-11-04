"""
AI Analysis Background Tasks

Celery tasks for asynchronous document analysis
"""
import logging
from datetime import datetime
import uuid

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.document import Document
from app.models.document_analysis import DocumentAnalysis
from app.services.ai_analysis_service import ai_service

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def analyze_document_async(self, document_id: str, file_path: str):
    """
    Analyze document asynchronously using Gemini AI
    
    Args:
        document_id: Document UUID
        file_path: Path to uploaded file
        
    Returns:
        Dict with analysis results
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Starting AI analysis for document {document_id}")
        
        # Get document
        document = db.query(Document).filter(
            Document.id == uuid.UUID(document_id)
        ).first()
        
        if not document:
            logger.error(f"Document {document_id} not found")
            return {
                "success": False,
                "error": "Document not found"
            }
        
        # Check if analysis already exists
        existing_analysis = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == uuid.UUID(document_id)
        ).first()
        
        if existing_analysis:
            logger.info(f"Analysis already exists for document {document_id}")
            return {
                "success": True,
                "message": "Analysis already exists",
                "analysis_id": str(existing_analysis.id)
            }
        
        # Perform AI analysis
        analysis_result = ai_service.analyze_document(
            file_path=file_path,
            file_type=document.file_type,
            filename=document.name
        )
        
        # Create DocumentAnalysis record
        analysis = DocumentAnalysis(
            document_id=uuid.UUID(document_id),
            summary=analysis_result["summary"],
            extracted_data=analysis_result["extracted_data"],
            ocr_text=analysis_result["ocr_text"],
            key_entities=analysis_result["key_entities"],
            confidence_score=analysis_result["confidence_score"],
            processing_time=analysis_result["processing_time"],
            analyzed_by=analysis_result["analyzed_by"],
            analyzed_at=datetime.utcnow()
        )
        
        db.add(analysis)
        
        # Update document status
        document.status = "analyzed"
        
        db.commit()
        
        logger.info(
            f"Successfully analyzed document {document_id} "
            f"in {analysis_result['processing_time']:.2f}s "
            f"(confidence: {analysis_result['confidence_score']:.2f})"
        )
        
        return {
            "success": True,
            "document_id": document_id,
            "analysis_id": str(analysis.id),
            "confidence_score": analysis_result["confidence_score"],
            "processing_time": analysis_result["processing_time"]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing document {document_id}: {e}", exc_info=True)
        
        # Retry on certain errors
        if "rate limit" in str(e).lower() or "timeout" in str(e).lower():
            raise self.retry(exc=e)
        
        # Update document status to failed
        try:
            document = db.query(Document).filter(
                Document.id == uuid.UUID(document_id)
            ).first()
            if document:
                document.status = "failed"
                db.commit()
        except:
            pass
        
        return {
            "success": False,
            "document_id": document_id,
            "error": str(e)
        }
        
    finally:
        db.close()


@celery_app.task
def analyze_pending_documents():
    """
    Analyze all pending documents
    
    Useful for batch processing or recovery
    """
    db = SessionLocal()
    
    try:
        logger.info("Checking for pending documents to analyze")
        
        # Find documents without analysis
        documents = db.query(Document).filter(
            Document.status.in_(['draft', 'review']),
            ~Document.id.in_(
                db.query(DocumentAnalysis.document_id)
            )
        ).limit(10).all()
        
        if not documents:
            logger.info("No pending documents found")
            return {
                "success": True,
                "documents_found": 0
            }
        
        # Trigger analysis for each
        for doc in documents:
            # Assume file is stored at uploads/{doc.id}/{doc.name}
            file_path = f"uploads/{doc.id}/{doc.name}"
            analyze_document_async.delay(str(doc.id), file_path)
        
        logger.info(f"Triggered analysis for {len(documents)} documents")
        
        return {
            "success": True,
            "documents_found": len(documents),
            "documents_triggered": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_pending_documents: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        db.close()
