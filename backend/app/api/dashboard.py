from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from app.services.kpi_service import KPIService
from app.models.kpi import KPIMetric, DashboardAlert
from app.models.document import Document
from app.models.workflow import RFI, Transmittal
from app.database import get_db

router = APIRouter(prefix="/api/v1/projects/{project_id}/dashboard", tags=["dashboard"])


@router.get("/kpis")
async def get_all_kpis(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get all KPIs for project"""
    kpis = KPIService.get_all_kpis(db, project_id)
    
    for kpi_id, kpi_data in kpis.items():
        if kpi_data['value'] >= kpi_data['target']:
            kpi_data['status'] = 'OK'
        elif kpi_data['value'] >= kpi_data['threshold_warning']:
            kpi_data['status'] = 'WARNING'
        else:
            kpi_data['status'] = 'CRITICAL'
        
        variance = ((kpi_data['value'] - kpi_data['target']) / kpi_data['target'] * 100) if kpi_data['target'] > 0 else 0
        kpi_data['variance'] = round(variance, 1)
    
    return kpis


@router.get("/summary")
async def get_dashboard_summary(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get dashboard summary with key metrics"""
    kpis = KPIService.get_all_kpis(db, project_id)
    
    total_docs = db.query(Document).filter(
        Document.project_id == uuid.UUID(project_id)
    ).count()
    
    docs_analyzed = db.query(Document).filter(
        Document.project_id == uuid.UUID(project_id),
        Document.status == "analyzed"
    ).count()
    
    total_rfis = db.query(RFI).filter(
        RFI.project_id == uuid.UUID(project_id)
    ).count()
    
    open_rfis = db.query(RFI).filter(
        RFI.project_id == uuid.UUID(project_id),
        RFI.status.in_(['open', 'in_progress'])
    ).count()
    
    overdue_rfis = db.query(RFI).filter(
        RFI.project_id == uuid.UUID(project_id),
        RFI.status == 'overdue'
    ).count()
    
    total_transmittals = db.query(Transmittal).filter(
        Transmittal.project_id == uuid.UUID(project_id)
    ).count()
    
    pending_transmittals = db.query(Transmittal).filter(
        Transmittal.project_id == uuid.UUID(project_id),
        Transmittal.status.in_(['draft', 'submitted', 'under_review'])
    ).count()
    
    for kpi_id, kpi_data in kpis.items():
        if kpi_data['value'] >= kpi_data['target']:
            kpi_data['status'] = 'OK'
        elif kpi_data['value'] >= kpi_data['threshold_warning']:
            kpi_data['status'] = 'WARNING'
        else:
            kpi_data['status'] = 'CRITICAL'
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "documents": {
            "total": total_docs,
            "analyzed": docs_analyzed,
            "pending": total_docs - docs_analyzed
        },
        "rfis": {
            "total": total_rfis,
            "open": open_rfis,
            "overdue": overdue_rfis,
            "closed": total_rfis - open_rfis - overdue_rfis
        },
        "transmittals": {
            "total": total_transmittals,
            "pending": pending_transmittals,
            "approved": total_transmittals - pending_transmittals
        },
        "kpis": {
            "ok": sum(1 for kpi in kpis.values() if kpi['value'] >= kpi['target']),
            "warning": sum(1 for kpi in kpis.values() if kpi['threshold_warning'] <= kpi['value'] < kpi['target']),
            "critical": sum(1 for kpi in kpis.values() if kpi['value'] < kpi['threshold_warning'])
        }
    }


@router.get("/kpi/{kpi_id}/history")
async def get_kpi_history(
    project_id: str,
    kpi_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get historical data for KPI (last N days)"""
    from sqlalchemy import func
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    history = db.query(
        func.date(KPIMetric.recorded_at).label('date'),
        func.avg(KPIMetric.value).label('avg_value'),
        func.max(KPIMetric.value).label('max_value'),
        func.min(KPIMetric.value).label('min_value')
    ).filter(
        KPIMetric.kpi_id == kpi_id,
        KPIMetric.project_id == uuid.UUID(project_id),
        KPIMetric.recorded_at >= cutoff_date
    ).group_by(
        func.date(KPIMetric.recorded_at)
    ).all()
    
    return {
        "kpi_id": kpi_id,
        "period_days": days,
        "data": [
            {
                "date": str(h[0]),
                "avg": round(h[1], 2),
                "max": round(h[2], 2),
                "min": round(h[3], 2)
            }
            for h in history
        ]
    }


@router.get("/alerts")
async def get_dashboard_alerts(
    project_id: str,
    acknowledged: bool = False,
    db: Session = Depends(get_db)
):
    """Get alerts (KPIs that are off target)"""
    query = db.query(DashboardAlert).filter(
        DashboardAlert.kpi_id.like('KPI-%')
    )
    
    if not acknowledged:
        query = query.filter(DashboardAlert.acknowledged == False)
    
    alerts = query.order_by(DashboardAlert.created_at.desc()).all()
    
    return {
        "total_alerts": len(alerts),
        "alerts": [
            {
                "id": str(a.id),
                "kpi_id": a.kpi_id,
                "type": a.alert_type,
                "message": a.message,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    project_id: str,
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Acknowledge alert"""
    alert = db.query(DashboardAlert).filter(
        DashboardAlert.id == uuid.UUID(alert_id)
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    
    return {"status": "acknowledged"}
