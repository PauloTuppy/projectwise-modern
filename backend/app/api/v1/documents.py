from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentVersionResponse
from app.services.document_service import DocumentService
from app.security import get_current_user

router = APIRouter()
document_service = DocumentService()

@router.post("/projects/{project_id}/documents", response_model=DocumentResponse)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    discipline: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await document_service.upload_document(
        db=db,
        project_id=project_id,
        file=file,
        user_id=str(current_user.id),
        name=name,
        description=description,
        discipline=discipline
    )

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    db_document = document_service.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.get("/projects/{project_id}/documents", response_model=List[DocumentResponse])
def list_project_documents(
    project_id: str,
    skip: int = 0,
    limit: int = 10,
    discipline: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return document_service.list_project_documents(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit,
        discipline=discipline,
        status=status
    )

@router.get("/documents/{document_id}/versions", response_model=List[DocumentVersionResponse])
def get_document_versions(document_id: str, db: Session = Depends(get_db)):
    return document_service.get_document_versions(db, document_id=document_id)

@router.post("/documents/{document_id}/restore/{version_id}", response_model=DocumentResponse)
def restore_version(document_id: str, version_id: str, db: Session = Depends(get_db)):
    try:
        return document_service.restore_version(db, document_id=document_id, version_id=version_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    document_service.delete_document(db, document_id=document_id)
    return {"message": "Document deleted successfully"}


@router.get("/documents/{document_id}/analysis")
async def get_document_analysis(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get AI analysis results for a document
    
    Returns analysis if available, or status if still processing
    """
    from app.models.document_analysis import DocumentAnalysis
    import uuid
    
    try:
        # Check if analysis exists
        analysis = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == uuid.UUID(document_id)
        ).first()
        
        if not analysis:
            # Check document status
            from app.models.document import Document
            document = db.query(Document).filter(
                Document.id == uuid.UUID(document_id)
            ).first()
            
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            return {
                "status": "processing",
                "message": "Analysis in progress"
            }
        
        # Return analysis results
        import json
        
        return {
            "status": "completed",
            "summary": analysis.summary,
            "extracted_data": json.loads(analysis.extracted_data) if analysis.extracted_data else {},
            "key_entities": analysis.key_entities or {},
            "confidence_score": analysis.confidence_score,
            "processing_time": analysis.processing_time,
            "analyzed_by": analysis.analyzed_by,
            "analyzed_at": analysis.analyzed_at.isoformat() if analysis.analyzed_at else None
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid document ID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analysis: {str(e)}")


@router.post("/documents/{document_id}/analyze")
async def trigger_document_analysis(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Manually trigger AI analysis for a document
    
    Useful for re-analyzing or analyzing documents that failed
    """
    from app.models.document import Document
    from app.tasks.ai_analysis_tasks import analyze_document_async
    import uuid
    
    try:
        # Check if document exists
        document = db.query(Document).filter(
            Document.id == uuid.UUID(document_id)
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Trigger analysis task
        file_path = f"uploads/{document.id}/{document.name}"
        task = analyze_document_async.delay(document_id, file_path)
        
        return {
            "status": "triggered",
            "message": "Analysis task started",
            "task_id": task.id,
            "document_id": document_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid document ID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering analysis: {str(e)}")
