from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService
from app.security import get_current_user

router = APIRouter()
notification_service = NotificationService()

@router.get("/notifications", response_model=List[NotificationResponse])
def list_notifications(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return notification_service.get_notifications(db, user_id=str(current_user.id))

@router.post("/notifications/{notification_id}/read")
def mark_as_read(notification_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    notification_service.mark_as_read(db, notification_id=notification_id, user_id=str(current_user.id))
    return {"message": "Notification marked as read"}
