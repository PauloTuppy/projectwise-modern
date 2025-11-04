from sqlalchemy.orm import Session
import uuid

from app.models.notification import Notification

class NotificationService:
    def get_notifications(self, db: Session, user_id: str):
        return db.query(Notification).filter(Notification.user_id == uuid.UUID(user_id)).all()

    def mark_as_read(self, db: Session, notification_id: str, user_id: str):
        db_notification = db.query(Notification).filter(
            Notification.id == uuid.UUID(notification_id),
            Notification.user_id == uuid.UUID(user_id)
        ).first()
        if db_notification:
            db_notification.read = True
            db.commit()
            db.refresh(db_notification)
        return db_notification
