from sqlalchemy.orm import Session
import uuid

from app.models.workflow import RFI, Transmittal
from app.schemas.workflow import RFICreate, RFIUpdate, TransmittalCreate

class WorkflowService:
    def create_rfi(self, db: Session, project_id: str, created_by: str, rfi_data: RFICreate):
        db_rfi = RFI(
            project_id=uuid.UUID(project_id),
            created_by=uuid.UUID(created_by),
            **rfi_data.dict()
        )
        db.add(db_rfi)
        db.commit()
        db.refresh(db_rfi)
        return db_rfi

    def list_project_rfis(self, db: Session, project_id: str):
        return db.query(RFI).filter(RFI.project_id == uuid.UUID(project_id)).all()

    def get_rfi(self, db: Session, rfi_id: str):
        return db.query(RFI).filter(RFI.id == uuid.UUID(rfi_id)).first()

    def update_rfi(self, db: Session, rfi_id: str, rfi_data: RFIUpdate):
        db_rfi = self.get_rfi(db, rfi_id)
        if db_rfi:
            update_data = rfi_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_rfi, key, value)
            db.commit()
            db.refresh(db_rfi)
        return db_rfi

    def create_transmittal(self, db: Session, project_id: str, created_by: str, transmittal_data: TransmittalCreate):
        db_transmittal = Transmittal(
            project_id=uuid.UUID(project_id),
            created_by=uuid.UUID(created_by),
            **transmittal_data.dict()
        )
        db.add(db_transmittal)
        db.commit()
        db.refresh(db_transmittal)
        return db_transmittal

    def list_project_transmittals(self, db: Session, project_id: str):
        return db.query(Transmittal).filter(Transmittal.project_id == uuid.UUID(project_id)).all()
