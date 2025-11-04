from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from app.models.document import Document, DocumentStatusEnum
from app.models.workflow import RFI, RFIStatusEnum

class DashboardService:
    def get_kpis(self, db: Session, project_id: str):
        total_documents = db.query(func.count(Document.id)).filter(Document.project_id == uuid.UUID(project_id)).scalar()
        documents_by_status = db.query(Document.status, func.count(Document.id)).filter(Document.project_id == uuid.UUID(project_id)).group_by(Document.status).all()
        open_rfis = db.query(func.count(RFI.id)).filter(RFI.project_id == uuid.UUID(project_id), RFI.status == RFIStatusEnum.OPEN).scalar()

        return {
            "total_documents": total_documents,
            "documents_by_status": {status: count for status, count in documents_by_status},
            "open_rfis": open_rfis
        }
