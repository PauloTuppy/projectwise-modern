from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.workflow import RFICreate, RFIUpdate, RFIResponse, TransmittalCreate, TransmittalUpdate, TransmittalResponse
from app.services.workflow_service import WorkflowService
from app.security import get_current_user

router = APIRouter()
workflow_service = WorkflowService()

@router.post("/projects/{project_id}/rfis", response_model=RFIResponse)
def create_rfi(
    project_id: str,
    rfi_data: RFICreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return workflow_service.create_rfi(
        db=db,
        project_id=project_id,
        created_by=str(current_user.id),
        rfi_data=rfi_data
    )

@router.get("/projects/{project_id}/rfis", response_model=List[RFIResponse])
def list_project_rfis(project_id: str, db: Session = Depends(get_db)):
    return workflow_service.list_project_rfis(db, project_id=project_id)

@router.get("/rfis/{rfi_id}", response_model=RFIResponse)
def get_rfi(rfi_id: str, db: Session = Depends(get_db)):
    db_rfi = workflow_service.get_rfi(db, rfi_id=rfi_id)
    if db_rfi is None:
        raise HTTPException(status_code=404, detail="RFI not found")
    return db_rfi

@router.put("/rfis/{rfi_id}", response_model=RFIResponse)
def update_rfi(rfi_id: str, rfi_data: RFIUpdate, db: Session = Depends(get_db)):
    return workflow_service.update_rfi(db, rfi_id=rfi_id, rfi_data=rfi_data)

@router.post("/projects/{project_id}/transmittals", response_model=TransmittalResponse)
def create_transmittal(
    project_id: str,
    transmittal_data: TransmittalCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return workflow_service.create_transmittal(
        db=db,
        project_id=project_id,
        created_by=str(current_user.id),
        transmittal_data=transmittal_data
    )

@router.get("/projects/{project_id}/transmittals", response_model=List[TransmittalResponse])
def list_project_transmittals(project_id: str, db: Session = Depends(get_db)):
    return workflow_service.list_project_transmittals(db, project_id=project_id)
