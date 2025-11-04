"""
KPI Background Tasks
ISO 9001:2015 Compliant

Automated tasks for calculating and storing KPIs, and monitoring thresholds.
Runs periodically via Celery Beat scheduler.
"""
import logging
from datetime import datetime, timedelta
from typing import List
import uuid

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.services.kpi_service import KPIService
from app.models.kpi import KPIMetric, KPIHistory, DashboardAlert
from app.models.project import Project


# Configure logging
logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60  # 1 minute
)
def calculate_and_store_kpis(self, project_id: str):
    """
    Calculate all KPIs and store in database
    
    This task:
    1. Calculates all 7 KPIs for the project
    2. Stores current values in kpi_metrics table
    3. Archives values in kpi_history table for trend analysis
    
    Runs every 5 minutes via Celery Beat
    
    Args:
        project_id: Project UUID as string
        
    Returns:
        Dict with success status and KPI count
        
    Raises:
        Retry on database errors (max 3 attempts)
    """
    db = SessionLocal()
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Starting KPI calculation for project {project_id}")
        
        # Verify project exists
        project = db.query(Project).filter(
            Project.id == uuid.UUID(project_id)
        ).first()
        
        if not project:
            logger.error(f"Project {project_id} not found")
            return {
                "success": False,
                "error": "Project not found"
            }
        
        # Calculate all KPIs
        kpis = KPIService.get_all_kpis(db, project_id)
        
        period_start = datetime.utcnow() - timedelta(minutes=5)
        period_end = datetime.utcnow()
        
        # Store each KPI
        for kpi_id, kpi_data in kpis.items():
            # Store in kpi_metrics (current snapshot)
            metric = KPIMetric(
                kpi_id=kpi_id,
                project_id=uuid.UUID(project_id),
                value=kpi_data['value'],
                target=kpi_data['target'],
                threshold_warning=kpi_data['threshold_warning'],
                threshold_critical=kpi_data['threshold_critical'],
                status=kpi_data['status'],
                recorded_at=datetime.utcnow(),
                period='real-time'
            )
            db.add(metric)
            
            # Store in kpi_history (archive for trends)
            history = KPIHistory(
                kpi_id=kpi_id,
                project_id=uuid.UUID(project_id),
                value=kpi_data['value'],
                target=kpi_data['target'],
                status=kpi_data['status'],
                recorded_at=datetime.utcnow(),
                period_start=period_start,
                period_end=period_end
            )
            db.add(history)
        
        # Commit all changes
        db.commit()
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(
            f"Successfully calculated and stored {len(kpis)} KPIs "
            f"for project {project_id} in {execution_time:.2f}s"
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "kpis_calculated": len(kpis),
            "execution_time": execution_time
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error calculating KPIs for project {project_id}: {e}", exc_info=True)
        
        # Retry on database errors
        if "database" in str(e).lower() or "connection" in str(e).lower():
            raise self.retry(exc=e)
        
        return {
            "success": False,
            "project_id": project_id,
            "error": str(e)
        }
        
    finally:
        db.close()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def check_kpi_thresholds(self, project_id: str):
    """
    Check KPI thresholds and generate alerts
    
    This task:
    1. Retrieves latest KPI values
    2. Checks if any KPIs are in WARNING or CRITICAL status
    3. Generates alerts for KPIs that crossed thresholds
    4. Avoids duplicate alerts for same KPI
    
    Runs every 15 minutes via Celery Beat
    
    Args:
        project_id: Project UUID as string
        
    Returns:
        Dict with success status and alerts generated
        
    Raises:
        Retry on database errors (max 3 attempts)
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Checking KPI thresholds for project {project_id}")
        
        # Get latest KPIs for project
        latest_kpis = db.query(KPIMetric).filter(
            KPIMetric.project_id == uuid.UUID(project_id)
        ).order_by(
            KPIMetric.kpi_id,
            KPIMetric.recorded_at.desc()
        ).all()
        
        # Group by kpi_id and get most recent
        kpi_dict = {}
        for kpi in latest_kpis:
            if kpi.kpi_id not in kpi_dict:
                kpi_dict[kpi.kpi_id] = kpi
        
        alerts_generated = 0
        
        # Check each KPI
        for kpi_id, kpi in kpi_dict.items():
            # Only alert on WARNING or CRITICAL status
            if kpi.status not in ['WARNING', 'CRITICAL']:
                continue
            
            # Check if alert already exists (unacknowledged)
            existing_alert = db.query(DashboardAlert).filter(
                DashboardAlert.kpi_id == kpi_id,
                DashboardAlert.acknowledged == False
            ).first()
            
            if existing_alert:
                logger.debug(f"Alert already exists for {kpi_id}, skipping")
                continue
            
            # Generate alert message
            if kpi.status == 'WARNING':
                message = (
                    f"{kpi_id} is below target: {kpi.value}{kpi_dict.get(kpi_id, {}).get('unit', '')} "
                    f"(target: {kpi.target})"
                )
            else:  # CRITICAL
                message = (
                    f"{kpi_id} is critically low: {kpi.value} "
                    f"(warning threshold: {kpi.threshold_warning})"
                )
            
            # Create new alert
            alert = DashboardAlert(
                kpi_id=kpi_id,
                alert_type=kpi.status.lower(),
                message=message,
                acknowledged=False,
                created_at=datetime.utcnow()
            )
            db.add(alert)
            alerts_generated += 1
            
            logger.info(f"Generated {kpi.status} alert for {kpi_id}")
        
        # Commit all alerts
        db.commit()
        
        logger.info(
            f"Threshold check complete for project {project_id}. "
            f"Generated {alerts_generated} new alerts"
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "alerts_generated": alerts_generated
        }
        
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error checking thresholds for project {project_id}: {e}",
            exc_info=True
        )
        
        # Retry on database errors
        if "database" in str(e).lower() or "connection" in str(e).lower():
            raise self.retry(exc=e)
        
        return {
            "success": False,
            "project_id": project_id,
            "error": str(e)
        }
        
    finally:
        db.close()


@celery_app.task
def calculate_kpis_for_all_projects():
    """
    Calculate KPIs for all active projects
    
    This is a convenience task that triggers KPI calculation
    for all active projects in the system.
    
    Returns:
        Dict with success status and project count
    """
    db = SessionLocal()
    
    try:
        logger.info("Starting KPI calculation for all active projects")
        
        # Get all active projects
        projects = db.query(Project).filter(
            Project.status == 'active'
        ).all()
        
        # Trigger calculation for each project
        for project in projects:
            calculate_and_store_kpis.delay(str(project.id))
        
        logger.info(f"Triggered KPI calculation for {len(projects)} projects")
        
        return {
            "success": True,
            "projects_triggered": len(projects)
        }
        
    except Exception as e:
        logger.error(f"Error triggering KPI calculations: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        db.close()


@celery_app.task
def check_thresholds_for_all_projects():
    """
    Check thresholds for all active projects
    
    This is a convenience task that triggers threshold checking
    for all active projects in the system.
    
    Returns:
        Dict with success status and project count
    """
    db = SessionLocal()
    
    try:
        logger.info("Starting threshold check for all active projects")
        
        # Get all active projects
        projects = db.query(Project).filter(
            Project.status == 'active'
        ).all()
        
        # Trigger threshold check for each project
        for project in projects:
            check_kpi_thresholds.delay(str(project.id))
        
        logger.info(f"Triggered threshold check for {len(projects)} projects")
        
        return {
            "success": True,
            "projects_triggered": len(projects)
        }
        
    except Exception as e:
        logger.error(f"Error triggering threshold checks: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        db.close()


@celery_app.task
def cleanup_old_kpi_data(days_to_keep: int = 1095):
    """
    Clean up old KPI data
    
    Removes KPI history older than specified days (default 3 years for ISO 9001:2015).
    Keeps kpi_metrics table intact (current values only).
    
    Args:
        days_to_keep: Number of days to retain (default 1095 = 3 years)
        
    Returns:
        Dict with success status and records deleted
    """
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        logger.info(f"Cleaning up KPI history older than {cutoff_date}")
        
        # Delete old history records
        deleted = db.query(KPIHistory).filter(
            KPIHistory.recorded_at < cutoff_date
        ).delete()
        
        db.commit()
        
        logger.info(f"Deleted {deleted} old KPI history records")
        
        return {
            "success": True,
            "records_deleted": deleted,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning up KPI data: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        db.close()
