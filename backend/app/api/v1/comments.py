from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.comment_service import CommentService
from app.security import get_current_user

router = APIRouter()
comment_service = CommentService()

@router.post("/documents/{document_id}/comments", response_model=CommentResponse)
def create_comment(
    document_id: str,
    comment_data: CommentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return comment_service.create_comment(
        db=db,
        document_id=document_id,
        author_id=str(current_user.id),
        comment=comment_data
    )

@router.get("/documents/{document_id}/comments", response_model=List[CommentResponse])
def list_document_comments(document_id: str, db: Session = Depends(get_db)):
    return comment_service.list_document_comments(db, document_id=document_id)

@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return comment_service.update_comment(
        db=db,
        comment_id=comment_id,
        author_id=str(current_user.id),
        comment_data=comment_data
    )

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    comment_service.delete_comment(db, comment_id=comment_id, author_id=str(current_user.id))
    return {"message": "Comment deleted successfully"}
