from sqlalchemy.orm import Session
import uuid

from app.models.user import User

class UserService:
    def get_user(self, db: Session, user_id: str):
        return db.query(User).filter(User.id == uuid.UUID(user_id)).first()

    def get_users(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
