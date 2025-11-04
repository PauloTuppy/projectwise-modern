"""
KPI Models for Dashboard
ISO 9001:2015 Compliant
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base


class KPIMetric(Base):
    """
    Current KPI values (latest snapshot)
    Stores the most recent measurement for each KPI
    """
    __tablename__ = "kpi_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # KPI Identification
    kpi_id = Column(String(50), nullable=False)  # KPI-001, KPI-002, etc.
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Values
    value = Column(Float, nullable=False)  # Current measured value
    target = Column(Float, nullable=False)  # Target value
    threshold_warning = Column(Float, nullable=False)  # Yellow alert threshold
    threshold_critical = Column(Float, nullable=False)  # Red alert threshold
    
    # Status
    status = Column(String(50), nullable=False)  # OK, WARNING, CRITICAL
    
    # Metadata
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    period = Column(String(50), nullable=False)  # daily, weekly, monthly, real-time
    
    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_kpi_metrics_project_id', 'project_id'),
        Index('idx_kpi_metrics_kpi_id', 'kpi_id'),
        Index('idx_kpi_metrics_recorded_at', 'recorded_at'),
        Index('idx_kpi_metrics_project_kpi', 'project_id', 'kpi_id'),
    )
    
    def __repr__(self):
        return f"<KPIMetric {self.kpi_id}: {self.value} (target: {self.target}, status: {self.status})>"


class KPIHistory(Base):
    """
    Historical KPI data for trend analysis
    Maintains time-series data for compliance and reporting
    ISO 9001:2015 Requirement: 3-year retention
    """
    __tablename__ = "kpi_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # KPI Identification
    kpi_id = Column(String(50), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Values
    value = Column(Float, nullable=False)
    target = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    
    # Time Period
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_kpi_history_project_id', 'project_id'),
        Index('idx_kpi_history_kpi_id', 'kpi_id'),
        Index('idx_kpi_history_recorded_at', 'recorded_at'),
        Index('idx_kpi_history_project_kpi_date', 'project_id', 'kpi_id', 'recorded_at'),
    )
    
    def __repr__(self):
        return f"<KPIHistory {self.kpi_id}: {self.value} at {self.recorded_at}>"


class DashboardAlert(Base):
    """
    Alerts generated when KPIs cross thresholds
    Supports acknowledgment workflow for issue tracking
    """
    __tablename__ = "dashboard_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Alert Information
    kpi_id = Column(String(50), nullable=False)
    alert_type = Column(String(50), nullable=False)  # warning, critical, info
    message = Column(String(500), nullable=False)
    
    # Acknowledgment Status
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_dashboard_alerts_kpi_id', 'kpi_id'),
        Index('idx_dashboard_alerts_acknowledged', 'acknowledged'),
        Index('idx_dashboard_alerts_created_at', 'created_at'),
        Index('idx_dashboard_alerts_kpi_acknowledged', 'kpi_id', 'acknowledged'),
    )
    
    def __repr__(self):
        return f"<DashboardAlert {self.kpi_id} ({self.alert_type}): {self.message[:50]}...>"
