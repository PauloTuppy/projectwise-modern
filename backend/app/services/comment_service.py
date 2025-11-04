from sqlalchemy.orm import Session
import uuid

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

class CommentService:
    def create_comment(self, db: Session, document_id: str, author_id: str, comment: CommentCreate):
        db_comment = Comment(
            document_id=uuid.UUID(document_id),
            author_id=uuid.UUID(author_id),
            **comment.dict()
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def list_document_comments(self, db: Session, document_id: str):
        return db.query(Comment).filter(Comment.document_id == uuid.UUID(document_id)).all()

    def update_comment(self, db: Session, comment_id: str, author_id: str, comment_data: CommentUpdate):
        db_comment = db.query(Comment).filter(Comment.id == uuid.UUID(comment_id), Comment.author_id == uuid.UUID(author_id)).first()
        if db_comment:
            update_data = comment_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_comment, key, value)
            db.commit()
            db.refresh(db_comment)
        return db_comment

    def delete_comment(self, db: Session, comment_id: str, author_id: str):
        db.query(Comment).filter(Comment.id == uuid.UUID(comment_id), Comment.author_id == uuid.UUID(author_id)).delete()
        db.commit()
