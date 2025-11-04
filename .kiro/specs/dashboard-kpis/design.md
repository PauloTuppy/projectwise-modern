# Design Document - Dashboard com KPIs

## Overview

The Dashboard with KPIs system provides real-time monitoring and visualization of key performance indicators for project management and quality assurance. The system follows a three-tier architecture with React frontend, FastAPI backend, and PostgreSQL database, implementing automated KPI calculation, threshold monitoring, and alert generation in compliance with ISO 9001:2015 standards.

### Key Design Principles

1. **Real-time First**: All KPIs update within 30 seconds of underlying data changes
2. **Automated Calculation**: Background tasks calculate KPIs without manual intervention
3. **Threshold-based Alerts**: Automatic alert generation when KPIs cross warning/critical thresholds
4. **Audit Compliance**: Complete historical tracking for ISO 9001:2015 compliance
5. **Performance Optimized**: Caching and efficient queries for sub-3-second load times
6. **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │  KPI Cards   │  │   Charts     │      │
│  │  Component   │  │  Component   │  │  (Recharts)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                           │                                  │
│                    Axios HTTP Client                         │
└───────────────────────────┼──────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   API Gateway   │
                    │   (FastAPI)     │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│  Dashboard API │  │  KPI Service │  │  Alert Service  │
│   Endpoints    │  │  (Business   │  │  (Threshold     │
│                │  │   Logic)     │  │   Monitoring)   │
└───────┬────────┘  └──────┬──────┘  └────────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │   PostgreSQL   │
                    │    Database    │
                    │                │
                    │  - kpi_metrics │
                    │  - kpi_history │
                    │  - alerts      │
                    └────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Celery Beat   │
                    │  (Scheduler)   │
                    │                │
                    │  - Calculate   │
                    │  - Monitor     │
                    └────────────────┘
```

### Data Flow

1. **KPI Calculation Flow**:
   - Celery Beat triggers calculation every 5 minutes
   - KPI Service queries source data (documents, RFIs, transmittals)
   - Service calculates KPI values and compares to thresholds
   - Results stored in kpi_metrics and kpi_history tables
   - Alert Service checks thresholds and generates alerts if needed

2. **Dashboard Display Flow**:
   - User opens dashboard page
   - Frontend requests KPI data via REST API
   - Backend retrieves latest KPI metrics from database
   - Frontend renders KPI cards with status colors
   - Auto-refresh every 30 seconds

3. **Historical Data Flow**:
   - User selects KPI for detailed view
   - Frontend requests historical data for selected period
   - Backend aggregates data by day from kpi_history table
   - Frontend renders line chart with trends

## Components and Interfaces

### Backend Components

#### 1. KPI Models (`backend/app/models/kpi.py`)

**KPIMetric Model**
```python
class KPIMetric(Base):
    """Current KPI values (latest snapshot)"""
    id: UUID
    kpi_id: str              # KPI-001, KPI-002, etc.
    project_id: UUID
    value: float             # Current measured value
    target: float            # Target value
    threshold_warning: float # Warning threshold
    threshold_critical: float # Critical threshold
    status: str              # OK, WARNING, CRITICAL
    recorded_at: datetime    # When measured
    period: str              # daily, weekly, monthly, real-time
```

**KPIHistory Model**
```python
class KPIHistory(Base):
    """Historical KPI data for trend analysis"""
    id: UUID
    kpi_id: str
    project_id: UUID
    value: float
    target: float
    status: str
    recorded_at: datetime
    period_start: datetime
    period_end: datetime
```

**DashboardAlert Model**
```python
class DashboardAlert(Base):
    """Alerts generated when KPIs cross thresholds"""
    id: UUID
    kpi_id: str
    alert_type: str          # warning, critical, info
    message: str
    acknowledged: bool
    acknowledged_by: UUID
    acknowledged_at: datetime
    created_at: datetime
```

#### 2. KPI Service (`backend/app/services/kpi_service.py`)

**Core Methods**:

```python
class KPIService:
    @staticmethod
    def calculate_upload_success_rate(db: Session, project_id: str, hours: int = 24) -> dict:
        """
        KPI-001: Upload Success Rate
        Formula: (total_uploads - failed_uploads) / total_uploads * 100
        Target: 99.5%
        """
        
    @staticmethod
    def calculate_ai_analysis_time(db: Session, project_id: str, percentile: int = 50) -> dict:
        """
        KPI-002: AI Analysis Time (P50)
        Formula: 50th percentile of processing_time
        Target: 30 seconds
        """
        
    @staticmethod
    def calculate_ai_accuracy(db: Session, project_id: str) -> dict:
        """
        KPI-003: AI Accuracy
        Formula: avg(confidence_score) * 100
        Target: 90%
        """
        
    @staticmethod
    def calculate_rfi_response_time(db: Session, project_id: str) -> dict:
        """
        KPI-004: RFI Response Time
        Formula: avg(responded_at - created_at) in days
        Target: 3 days
        """
        
    @staticmethod
    def calculate_rfi_closure_rate(db: Session, project_id: str) -> dict:
        """
        KPI-005: RFI Closure Rate
        Formula: closed_rfis / total_rfis * 100
        Target: 95%
        """
        
    @staticmethod
    def calculate_transmittal_approval_time(db: Session, project_id: str) -> dict:
        """
        KPI-006: Transmittal Approval Time
        Formula: avg(approved_at - submitted_at) in days
        Target: 5 days
        """
        
    @staticmethod
    def calculate_on_time_completion(db: Session, project_id: str) -> dict:
        """
        KPI-007: On-time Completion Rate
        Formula: items_completed_on_time / total_completed * 100
        Target: 90%
        """
        
    @staticmethod
    def get_all_kpis(db: Session, project_id: str) -> dict:
        """Calculate all KPIs and return as dictionary"""
        
    @staticmethod
    def determine_status(value: float, target: float, threshold_warning: float, threshold_critical: float) -> str:
        """Determine KPI status based on thresholds"""
        if value >= target:
            return "OK"
        elif value >= threshold_warning:
            return "WARNING"
        else:
            return "CRITICAL"
```

#### 3. Dashboard API (`backend/app/api/dashboard.py`)

**Endpoints**:

```python
GET /api/v1/projects/{project_id}/dashboard/kpis
    Response: {
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

GET /api/v1/projects/{project_id}/dashboard/summary
    Response: {
        "timestamp": "2025-11-03T10:30:00Z",
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

GET /api/v1/projects/{project_id}/dashboard/kpi/{kpi_id}/history?days=7
    Response: {
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

GET /api/v1/projects/{project_id}/dashboard/alerts?acknowledged=false
    Response: {
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

POST /api/v1/projects/{project_id}/dashboard/alerts/{alert_id}/acknowledge
    Request: {}
    Response: {
        "status": "acknowledged"
    }
```

#### 4. Background Tasks (`backend/app/tasks/kpi_tasks.py`)

**Celery Tasks**:

```python
@celery_app.task
def calculate_and_store_kpis(project_id: str):
    """
    Calculate all KPIs and store in database
    Runs every 5 minutes via Celery Beat
    """
    db = SessionLocal()
    try:
        kpis = KPIService.get_all_kpis(db, project_id)
        
        for kpi_id, kpi_data in kpis.items():
            # Store in kpi_metrics (current)
            metric = KPIMetric(
                kpi_id=kpi_id,
                project_id=project_id,
                value=kpi_data['value'],
                target=kpi_data['target'],
                threshold_warning=kpi_data['threshold_warning'],
                threshold_critical=kpi_data['threshold_critical'],
                status=kpi_data['status'],
                recorded_at=datetime.utcnow(),
                period='real-time'
            )
            db.add(metric)
            
            # Store in kpi_history (archive)
            history = KPIHistory(
                kpi_id=kpi_id,
                project_id=project_id,
                value=kpi_data['value'],
                target=kpi_data['target'],
                status=kpi_data['status'],
                recorded_at=datetime.utcnow(),
                period_start=datetime.utcnow() - timedelta(minutes=5),
                period_end=datetime.utcnow()
            )
            db.add(history)
        
        db.commit()
    finally:
        db.close()

@celery_app.task
def check_kpi_thresholds(project_id: str):
    """
    Check KPI thresholds and generate alerts
    Runs every 15 minutes via Celery Beat
    """
    db = SessionLocal()
    try:
        # Get latest KPIs
        latest_kpis = db.query(KPIMetric).filter(
            KPIMetric.project_id == project_id
        ).all()
        
        for kpi in latest_kpis:
            # Check if alert already exists
            existing_alert = db.query(DashboardAlert).filter(
                DashboardAlert.kpi_id == kpi.kpi_id,
                DashboardAlert.acknowledged == False
            ).first()
            
            if kpi.status in ['WARNING', 'CRITICAL'] and not existing_alert:
                # Generate new alert
                alert = DashboardAlert(
                    kpi_id=kpi.kpi_id,
                    alert_type=kpi.status.lower(),
                    message=f"{kpi.kpi_id} is {kpi.status}: {kpi.value} (target: {kpi.target})",
                    acknowledged=False,
                    created_at=datetime.utcnow()
                )
                db.add(alert)
        
        db.commit()
    finally:
        db.close()
```

### Frontend Components

#### 1. Dashboard Component (`frontend/src/components/Dashboard.tsx`)

**Main Dashboard Container**:

```typescript
interface DashboardProps {
    projectId: string;
}

export const Dashboard: React.FC<DashboardProps> = ({ projectId }) => {
    // State
    const [kpis, setKpis] = useState<Record<string, KPI>>({});
    const [summary, setSummary] = useState<DashboardData | null>(null);
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedKpi, setSelectedKpi] = useState('KPI-001');
    const [kpiHistory, setKpiHistory] = useState<HistoricalData[]>([]);
    
    // Effects
    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 30000); // 30s refresh
        return () => clearInterval(interval);
    }, [projectId]);
    
    // Methods
    const fetchDashboardData = async () => {
        // Fetch KPIs, summary, and alerts in parallel
    };
    
    const fetchKpiHistory = async () => {
        // Fetch historical data for selected KPI
    };
    
    // Render
    return (
        <div>
            {/* KPI Status Summary */}
            {/* Main Metrics Cards */}
            {/* KPI Cards Grid */}
            {/* Historical Chart */}
            {/* Alerts List */}
        </div>
    );
};
```

**Component Structure**:
- **KPI Status Summary**: 3 cards showing OK/WARNING/CRITICAL counts
- **Main Metrics**: 4 cards showing documents, RFIs, transmittals, alerts
- **KPI Cards Grid**: 2-column grid of all KPI cards
- **Historical Chart**: Line chart showing 7-day trend for selected KPI
- **Alerts List**: List of unacknowledged alerts

#### 2. KPI Card Component (`frontend/src/components/KPICard.tsx`)

**Individual KPI Display**:

```typescript
interface KPICardProps {
    kpiId: string;
    value: number;
    target: number;
    unit: string;
    status: 'OK' | 'WARNING' | 'CRITICAL';
    variance: number;
    onClick?: () => void;
}

export const KPICard: React.FC<KPICardProps> = ({
    kpiId, value, target, unit, status, variance, onClick
}) => {
    return (
        <div className={`kpi-card ${getStatusColor(status)}`} onClick={onClick}>
            {/* Status Badge */}
            {/* Value Display */}
            {/* Progress Bar */}
            {/* Variance Indicator */}
        </div>
    );
};
```

**Visual Design**:
- Border color indicates status (green/yellow/red)
- Large value display with unit
- Progress bar showing value vs target
- Variance percentage with up/down indicator
- Click to view historical trend

#### 3. Chart Components

**Using Recharts Library**:

```typescript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Historical Trend Chart
<ResponsiveContainer width="100%" height={300}>
    <LineChart data={kpiHistory}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="avg" stroke="#3b82f6" name="Average" />
        <Line type="monotone" dataKey="max" stroke="#10b981" name="Max" />
        <Line type="monotone" dataKey="min" stroke="#ef4444" name="Min" />
    </LineChart>
</ResponsiveContainer>
```

## Data Models

### Database Schema

```sql
-- KPI Metrics (Current Values)
CREATE TABLE kpi_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id VARCHAR(50) NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id),
    value FLOAT NOT NULL,
    target FLOAT NOT NULL,
    threshold_warning FLOAT NOT NULL,
    threshold_critical FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    period VARCHAR(50) NOT NULL,
    CONSTRAINT fk_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_kpi_metrics_project ON kpi_metrics(project_id);
CREATE INDEX idx_kpi_metrics_kpi_id ON kpi_metrics(kpi_id);
CREATE INDEX idx_kpi_metrics_recorded_at ON kpi_metrics(recorded_at);

-- KPI History (Time Series)
CREATE TABLE kpi_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id VARCHAR(50) NOT NULL,
    project_id UUID NOT NULL REFERENCES projects(id),
    value FLOAT NOT NULL,
    target FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    CONSTRAINT fk_project_history FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_kpi_history_project ON kpi_history(project_id);
CREATE INDEX idx_kpi_history_kpi_id ON kpi_history(kpi_id);
CREATE INDEX idx_kpi_history_recorded_at ON kpi_history(recorded_at);

-- Dashboard Alerts
CREATE TABLE dashboard_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    message VARCHAR(500) NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_alerts_kpi_id ON dashboard_alerts(kpi_id);
CREATE INDEX idx_alerts_acknowledged ON dashboard_alerts(acknowledged);
CREATE INDEX idx_alerts_created_at ON dashboard_alerts(created_at);
```

### Data Retention Policy

- **kpi_metrics**: Keep latest 30 days, older records moved to kpi_history
- **kpi_history**: Keep 3 years for ISO 9001:2015 compliance
- **dashboard_alerts**: Keep acknowledged alerts for 90 days, unacknowledged indefinitely

## Error Handling

### Backend Error Handling

```python
@router.get("/api/v1/projects/{project_id}/dashboard/kpis")
async def get_all_kpis(project_id: str, db: Session = Depends(get_db)):
    try:
        kpis = KPIService.get_all_kpis(db, project_id)
        return kpis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching KPIs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Frontend Error Handling

```typescript
const fetchDashboardData = async () => {
    try {
        setLoading(true);
        setError(null);
        
        const [kpiResponse, summaryResponse, alertsResponse] = await Promise.all([
            axios.get(`/api/v1/projects/${projectId}/dashboard/kpis`),
            axios.get(`/api/v1/projects/${projectId}/dashboard/summary`),
            axios.get(`/api/v1/projects/${projectId}/dashboard/alerts`)
        ]);
        
        setKpis(kpiResponse.data);
        setSummary(summaryResponse.data);
        setAlerts(alertsResponse.data.alerts);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Retrying...');
        
        // Retry after 5 seconds
        setTimeout(fetchDashboardData, 5000);
    } finally {
        setLoading(false);
    }
};
```

### Graceful Degradation

1. **Partial Data Failure**: If one KPI fails to calculate, show others with error indicator
2. **API Unavailable**: Display cached data with "offline" indicator
3. **Calculation Timeout**: Use last known value with timestamp
4. **Database Connection Loss**: Queue calculations for retry

## Testing Strategy

### Unit Tests

**Backend Tests** (`backend/tests/test_kpi_service.py`):

```python
def test_calculate_upload_success_rate():
    """Test KPI-001 calculation"""
    # Setup: Create test documents
    # Execute: Calculate KPI
    # Assert: Verify correct percentage
    
def test_calculate_ai_analysis_time():
    """Test KPI-002 calculation"""
    # Setup: Create test analyses with processing times
    # Execute: Calculate P50
    # Assert: Verify correct percentile
    
def test_determine_status():
    """Test status determination logic"""
    # Test OK status
    # Test WARNING status
    # Test CRITICAL status
```

**Frontend Tests** (`frontend/src/components/__tests__/Dashboard.test.tsx`):

```typescript
describe('Dashboard Component', () => {
    it('should render KPI cards', () => {
        // Render with mock data
        // Assert cards are displayed
    });
    
    it('should refresh data every 30 seconds', () => {
        // Mock timer
        // Assert fetch called at intervals
    });
    
    it('should handle API errors gracefully', () => {
        // Mock API error
        // Assert error message displayed
    });
});
```

### Integration Tests

```python
def test_dashboard_api_integration():
    """Test complete dashboard API flow"""
    # Create test project with data
    # Call dashboard endpoints
    # Verify response structure and values
    
def test_kpi_calculation_and_storage():
    """Test KPI calculation task"""
    # Trigger Celery task
    # Verify data stored in database
    # Verify historical records created
```

### Performance Tests

```python
def test_dashboard_load_time():
    """Verify dashboard loads within 3 seconds"""
    start = time.time()
    response = client.get(f"/api/v1/projects/{project_id}/dashboard/kpis")
    duration = time.time() - start
    assert duration < 3.0
    
def test_kpi_calculation_time():
    """Verify KPI calculation completes within 30 seconds"""
    start = time.time()
    calculate_and_store_kpis(project_id)
    duration = time.time() - start
    assert duration < 30.0
```

## Performance Optimization

### Database Optimization

1. **Indexes**: Create indexes on frequently queried columns (project_id, kpi_id, recorded_at)
2. **Partitioning**: Partition kpi_history by month for faster queries
3. **Aggregation**: Pre-aggregate daily statistics to reduce calculation time
4. **Connection Pooling**: Use SQLAlchemy connection pool (min=5, max=20)

### Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_kpis(project_id: str, cache_key: str):
    """Cache KPI data for 30 seconds"""
    return KPIService.get_all_kpis(db, project_id)

# Generate cache key that changes every 30 seconds
cache_key = f"{project_id}_{int(datetime.utcnow().timestamp() / 30)}"
kpis = get_cached_kpis(project_id, cache_key)
```

### Frontend Optimization

1. **Code Splitting**: Lazy load chart components
2. **Memoization**: Use React.memo for KPI cards
3. **Debouncing**: Debounce auto-refresh to avoid excessive requests
4. **Virtual Scrolling**: For large alert lists

## Security Considerations

### Authentication & Authorization

```python
@router.get("/api/v1/projects/{project_id}/dashboard/kpis")
async def get_all_kpis(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user has access to project
    if not has_project_access(current_user, project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    kpis = KPIService.get_all_kpis(db, project_id)
    return kpis
```

### Data Validation

```python
from pydantic import BaseModel, validator

class KPIMetricCreate(BaseModel):
    kpi_id: str
    value: float
    target: float
    
    @validator('kpi_id')
    def validate_kpi_id(cls, v):
        if not v.startswith('KPI-'):
            raise ValueError('Invalid KPI ID format')
        return v
    
    @validator('value', 'target')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError('Value must be positive')
        return v
```

## ISO 9001:2015 Compliance Mapping

| ISO Requirement | Implementation | Evidence |
|-----------------|----------------|----------|
| 4.4.1 QMS Processes | KPI tracking system | kpi_metrics table |
| 7.1.5 Monitoring Resources | Real-time dashboard | Dashboard component |
| 7.2 Competence | Alert notifications | dashboard_alerts table |
| 8.1 Operational Planning | KPI targets and thresholds | KPI configuration |
| 9.1.1 Performance Evaluation | KPI calculations | KPIService methods |
| 9.2.1 Internal Audit | Historical data | kpi_history table |
| 10.2.1 Nonconformity | Alert system | Alert generation task |
| 10.3 Continual Improvement | Trend analysis | Historical charts |

## Deployment Considerations

### Environment Variables

```bash
# Backend (.env)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
KPI_CALCULATION_INTERVAL=300  # 5 minutes
ALERT_CHECK_INTERVAL=900      # 15 minutes
KPI_HISTORY_RETENTION_DAYS=1095  # 3 years
```

### Celery Beat Configuration

```python
# backend/app/celery_config.py
from celery.schedules import crontab

beat_schedule = {
    'calculate-kpis-every-5-minutes': {
        'task': 'app.tasks.kpi_tasks.calculate_and_store_kpis',
        'schedule': crontab(minute='*/5'),
        'args': (project_id,)
    },
    'check-thresholds-every-15-minutes': {
        'task': 'app.tasks.kpi_tasks.check_kpi_thresholds',
        'schedule': crontab(minute='*/15'),
        'args': (project_id,)
    },
}
```

### Monitoring & Logging

```python
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def calculate_and_store_kpis(project_id: str):
    logger.info(f"Starting KPI calculation for project {project_id}")
    try:
        # Calculation logic
        logger.info(f"Successfully calculated KPIs for project {project_id}")
    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}", exc_info=True)
        raise
```

---

**Document Control**
- Version: 1.0
- Date: 2025-11-03
- Status: Draft
- Based on: requirements.md v1.0
