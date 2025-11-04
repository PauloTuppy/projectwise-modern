"""
Dashboard API Endpoints
ISO 9001:2015 Compliant

Provides REST API endpoints for dashboard KPIs, summary metrics,
historical data, and alert management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app.database import get_db
from app.services.kpi_service import KPIService
from app.models.kpi import KPIMetric, DashboardAlert
from app.models.document import Document
from app.models.workflow import RFI, Transmittal


router = APIRouter(prefix="/projects/{project_id}/dashboard", tags=["dashboard"])


@router.get("/kpis")
async def get_all_kpis(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all KPIs for a project
    
    Returns current values, targets, thresholds, status, and variance
    for all 7 KPIs.
    
    Args:
        project_id: Project UUID
        db: Database session
        
    Returns:
        Dictionary of all KPIs with calculated values
        
    Example Response:
        {
            "KPI-001": {
                "kpi_id": "KPI-001",
                "value": 99.7,
                "target": 99.5,
                "threshold_warning": 99.0,
                "threshold_critical": 98.0,
                "status": "OK",
                "variance": 0.2,
                "unit": "%"
            },
            ...
        }
    """
    try:
        kpis = KPIService.get_all_kpis(db, project_id)
        return kpis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating KPIs: {str(e)}"
        )


@router.get("/summary")
async def get_dashboard_summary(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary with key metrics
    
    Provides high-level overview of project status including
    document counts, RFI counts, transmittal counts, and KPI status summary.
    
    Args:
        project_id: Project UUID
        db: Database session
        
    Returns:
        Summary object with counts and KPI status
        
    Example Response:
        {
            "timestamp": "2025-11-03T22:30:00Z",
            "documents": {
                "total": 150,
                "analyzed": 145,
                "pending": 5
            },
            "rfis": {
                "total": 45,
                "open": 12,
                "overdue": 3,
                "closed": 30
            },
            "transmittals": {
                "total": 28,
                "pending": 8,
                "approved": 20
            },
            "kpis": {
                "ok": 5,
                "warning": 1,
                "critical": 1
            }
        }
    """
    try:
        project_uuid = uuid.UUID(project_id)
        
        # Get KPIs for status summary
        kpis = KPIService.get_all_kpis(db, project_id)
        
        # Count documents
        total_docs = db.query(func.count(Document.id)).filter(
            Document.project_id == project_uuid,
            Document.deleted_at.is_(None)  # Exclude soft-deleted
        ).scalar() or 0
        
        docs_analyzed = db.query(func.count(Document.id)).filter(
            Document.project_id == project_uuid,
            Document.status.in_(['approved', 'review']),
            Document.deleted_at.is_(None)
        ).scalar() or 0
        
        # Count RFIs
        total_rfis = db.query(func.count(RFI.id)).filter(
            RFI.project_id == project_uuid
        ).scalar() or 0
        
        open_rfis = db.query(func.count(RFI.id)).filter(
            RFI.project_id == project_uuid,
            RFI.status.in_(['open', 'answered'])
        ).scalar() or 0
        
        # Overdue RFIs (due_date < now and status != closed)
        overdue_rfis = db.query(func.count(RFI.id)).filter(
            RFI.project_id == project_uuid,
            RFI.status != 'closed',
            RFI.due_date < datetime.utcnow()
        ).scalar() or 0
        
        closed_rfis = db.query(func.count(RFI.id)).filter(
            RFI.project_id == project_uuid,
            RFI.status == 'closed'
        ).scalar() or 0
        
        # Count Transmittals
        total_transmittals = db.query(func.count(Transmittal.id)).filter(
            Transmittal.project_id == project_uuid
        ).scalar() or 0
        
        pending_transmittals = db.query(func.count(Transmittal.id)).filter(
            Transmittal.project_id == project_uuid,
            Transmittal.status.in_(['draft', 'submitted'])
        ).scalar() or 0
        
        approved_transmittals = db.query(func.count(Transmittal.id)).filter(
            Transmittal.project_id == project_uuid,
            Transmittal.status == 'approved'
        ).scalar() or 0
        
        # Count KPI statuses
        kpi_status_counts = {
            "ok": sum(1 for kpi in kpis.values() if kpi['status'] == 'OK'),
            "warning": sum(1 for kpi in kpis.values() if kpi['status'] == 'WARNING'),
            "critical": sum(1 for kpi in kpis.values() if kpi['status'] == 'CRITICAL')
        }
        
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
                "closed": closed_rfis
            },
            "transmittals": {
                "total": total_transmittals,
                "pending": pending_transmittals,
                "approved": approved_transmittals
            },
            "kpis": kpi_status_counts
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid project ID: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard summary: {str(e)}"
        )


@router.get("/kpi/{kpi_id}/history")
async def get_kpi_history(
    project_id: str,
    kpi_id: str,
    days: int = Query(default=7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get historical data for a specific KPI
    
    Returns time-series data aggregated by day for the specified period.
    
    Args:
        project_id: Project UUID
        kpi_id: KPI identifier (e.g., KPI-001)
        days: Number of days to retrieve (default 7, max 365)
        db: Database session
        
    Returns:
        Historical data with daily aggregates (avg, max, min)
        
    Example Response:
        {
            "kpi_id": "KPI-001",
            "period_days": 7,
            "data": [
                {
                    "date": "2025-11-03",
                    "avg": 99.5,
                    "max": 99.8,
                    "min": 99.2
                },
                ...
            ]
        }
    """
    try:
        project_uuid = uuid.UUID(project_id)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query historical data
        history = db.query(
            func.date(KPIMetric.recorded_at).label('date'),
            func.avg(KPIMetric.value).label('avg_value'),
            func.max(KPIMetric.value).label('max_value'),
            func.min(KPIMetric.value).label('min_value')
        ).filter(
            KPIMetric.kpi_id == kpi_id,
            KPIMetric.project_id == project_uuid,
            KPIMetric.recorded_at >= cutoff_date
        ).group_by(
            func.date(KPIMetric.recorded_at)
        ).order_by(
            func.date(KPIMetric.recorded_at)
        ).all()
        
        return {
            "kpi_id": kpi_id,
            "period_days": days,
            "data": [
                {
                    "date": str(h.date),
                    "avg": round(h.avg_value, 2),
                    "max": round(h.max_value, 2),
                    "min": round(h.min_value, 2)
                }
                for h in history
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching KPI history: {str(e)}"
        )


@router.get("/alerts")
async def get_dashboard_alerts(
    project_id: str,
    acknowledged: Optional[bool] = Query(default=False),
    db: Session = Depends(get_db)
):
    """
    Get dashboard alerts
    
    Returns alerts generated when KPIs cross warning or critical thresholds.
    Can filter by acknowledgment status.
    
    Args:
        project_id: Project UUID (currently not filtered by project)
        acknowledged: Filter by acknowledged status (default False = unacknowledged only)
        db: Database session
        
    Returns:
        List of alerts with metadata
        
    Example Response:
        {
            "total_alerts": 3,
            "alerts": [
                {
                    "id": "uuid",
                    "kpi_id": "KPI-004",
                    "type": "warning",
                    "message": "RFI Response Time exceeded target",
                    "created_at": "2025-11-03T09:15:00Z"
                },
                ...
            ]
        }
    """
    try:
        # Build query
        query = db.query(DashboardAlert).filter(
            DashboardAlert.kpi_id.like('KPI-%')
        )
        
        # Filter by acknowledged status
        if not acknowledged:
            query = query.filter(DashboardAlert.acknowledged == False)
        
        # Order by most recent first
        alerts = query.order_by(DashboardAlert.created_at.desc()).all()
        
        return {
            "total_alerts": len(alerts),
            "alerts": [
                {
                    "id": str(alert.id),
                    "kpi_id": alert.kpi_id,
                    "type": alert.alert_type,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat(),
                    "acknowledged": alert.acknowledged,
                    "acknowledged_by": str(alert.acknowledged_by) if alert.acknowledged_by else None,
                    "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching alerts: {str(e)}"
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    project_id: str,
    alert_id: str,
    db: Session = Depends(get_db),
    # TODO: Add current_user dependency when auth is implemented
    # current_user: User = Depends(get_current_user)
):
    """
    Acknowledge an alert
    
    Marks an alert as acknowledged and records who acknowledged it and when.
    
    Args:
        project_id: Project UUID
        alert_id: Alert UUID
        db: Database session
        
    Returns:
        Success status
        
    Example Response:
        {
            "status": "acknowledged",
            "alert_id": "uuid",
            "acknowledged_at": "2025-11-03T22:30:00Z"
        }
    """
    try:
        alert_uuid = uuid.UUID(alert_id)
        
        # Find alert
        alert = db.query(DashboardAlert).filter(
            DashboardAlert.id == alert_uuid
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert
        alert.acknowledged = True
        # TODO: Use actual current_user.id when auth is implemented
        # alert.acknowledged_by = current_user.id
        alert.acknowledged_by = None  # Placeholder
        alert.acknowledged_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "status": "acknowledged",
            "alert_id": str(alert.id),
            "acknowledged_at": alert.acknowledged_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid alert ID: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error acknowledging alert: {str(e)}"
        )
