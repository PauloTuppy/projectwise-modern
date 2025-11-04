# Implementation Plan - Dashboard com KPIs

## Overview

This implementation plan breaks down the Dashboard with KPIs feature into discrete, actionable coding tasks. Each task builds incrementally on previous work, starting with backend models and services, then API endpoints, background tasks, and finally frontend components.

---

## Tasks

- [x] 1. Create KPI database models and migrations



  - Create SQLAlchemy models for KPIMetric, KPIHistory, and DashboardAlert
  - Define relationships with existing Project model
  - Add indexes for performance optimization
  - Generate Alembic migration for new tables





  - _Requirements: 1.1, 1.4, 14.1, 14.2, 14.3_

- [ ] 2. Implement KPI calculation service
  - [x] 2.1 Create KPIService class with base structure

    - Create `backend/app/services/kpi_service.py` file
    - Implement helper method for status determination (OK/WARNING/CRITICAL)
    - Implement helper method for variance calculation
    - _Requirements: 2.1, 2.2, 2.3_


  - [ ] 2.2 Implement upload success rate calculation (KPI-001)
    - Query documents from last 24 hours
    - Calculate success rate formula: (total - failed) / total * 100
    - Return dict with value, target (99.5%), thresholds, and unit
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_


  - [ ] 2.3 Implement AI analysis time calculation (KPI-002)
    - Query DocumentAnalysis processing times
    - Calculate 50th percentile (P50) of processing times
    - Return dict with value, target (30s), thresholds, and unit

    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 2.4 Implement AI accuracy calculation (KPI-003)
    - Query DocumentAnalysis confidence scores
    - Calculate average confidence score * 100

    - Return dict with value, target (90%), thresholds, and unit
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 2.5 Implement RFI response time calculation (KPI-004)
    - Query RFIs with responded_at not null

    - Calculate average days between created_at and responded_at
    - Return dict with value, target (3 days), thresholds, and unit
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 2.6 Implement RFI closure rate calculation (KPI-005)

    - Query total RFIs and closed RFIs
    - Calculate closure rate: closed / total * 100
    - Return dict with value, target (95%), thresholds, and unit
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


  - [ ] 2.7 Implement transmittal approval time calculation (KPI-006)
    - Query Transmittals with approved_at not null
    - Calculate average days between submitted_at and approved_at
    - Return dict with value, target (5 days), thresholds, and unit





    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ] 2.8 Implement on-time completion calculation (KPI-007)
    - Query completed RFIs and Transmittals

    - Calculate percentage completed by due date
    - Return dict with value, target (90%), thresholds, and unit
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 2.9 Implement get_all_kpis aggregation method

    - Call all individual KPI calculation methods
    - Add status determination for each KPI
    - Add variance calculation for each KPI
    - Return dictionary of all KPIs
    - _Requirements: 1.1, 1.4, 1.5_

- [x] 3. Create dashboard API endpoints

  - [ ] 3.1 Create dashboard router and base structure
    - Create `backend/app/api/v1/dashboard.py` file
    - Define APIRouter with prefix `/api/v1/projects/{project_id}/dashboard`
    - Add dependency injection for database session
    - _Requirements: 1.1_


  - [ ] 3.2 Implement GET /kpis endpoint
    - Call KPIService.get_all_kpis()
    - Return all KPIs with current values and status
    - Add error handling for invalid project_id
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_


  - [ ] 3.3 Implement GET /summary endpoint
    - Query counts for documents (total, analyzed, pending)
    - Query counts for RFIs (total, open, overdue, closed)
    - Query counts for transmittals (total, pending, approved)
    - Calculate KPI status summary (ok, warning, critical)
    - Return summary object with timestamp

    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_






  - [ ] 3.4 Implement GET /kpi/{kpi_id}/history endpoint
    - Query KPIHistory table for specified kpi_id and date range
    - Aggregate data by day (avg, max, min)
    - Return time series data for charting
    - Support days parameter (default 7, max 90)

    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ] 3.5 Implement GET /alerts endpoint
    - Query DashboardAlert table
    - Filter by acknowledged status (default false)
    - Order by created_at descending
    - Return alerts with count
    - _Requirements: 12.3, 12.5_


  - [ ] 3.6 Implement POST /alerts/{alert_id}/acknowledge endpoint
    - Find alert by ID
    - Update acknowledged flag to true
    - Record acknowledged_by user ID and timestamp
    - Return success status
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_


  - [ ] 3.7 Add dashboard router to main FastAPI app
    - Import dashboard router in `backend/app/main.py`
    - Include router with app.include_router()





    - _Requirements: 1.1_

- [ ] 4. Implement background tasks for automated KPI calculation
  - [ ] 4.1 Set up Celery configuration
    - Create `backend/app/celery_config.py` if not exists
    - Configure Celery Beat schedule for periodic tasks

    - Add KPI calculation task to run every 5 minutes
    - Add threshold check task to run every 15 minutes
    - _Requirements: 15.1, 15.2_

  - [ ] 4.2 Create KPI calculation Celery task
    - Create `backend/app/tasks/kpi_tasks.py` file
    - Implement calculate_and_store_kpis task
    - Call KPIService.get_all_kpis() for project

    - Store results in kpi_metrics table (current values)
    - Store results in kpi_history table (archive)
    - Add error handling and logging
    - Ensure task completes within 30 seconds
    - _Requirements: 15.1, 15.3, 15.4, 15.5_


  - [ ] 4.3 Create threshold monitoring Celery task
    - Implement check_kpi_thresholds task in kpi_tasks.py
    - Query latest KPIMetric records
    - Check if KPI status is WARNING or CRITICAL
    - Generate DashboardAlert if no existing unacknowledged alert
    - Add error handling and logging

    - _Requirements: 12.1, 12.2, 15.2_

  - [ ] 4.4 Add task monitoring and error recovery
    - Implement retry logic for failed tasks (max 3 retries)
    - Add exponential backoff for retries
    - Log task execution times and failures

    - _Requirements: 15.3, 20.1_

- [ ] 5. Create frontend Dashboard component
  - [ ] 5.1 Create Dashboard component structure
    - Create `frontend/src/components/Dashboard.tsx` file
    - Define TypeScript interfaces for KPI, DashboardData, Alert
    - Set up component state (kpis, summary, alerts, loading, error)

    - Add projectId prop
    - _Requirements: 1.1, 16.1_

  - [ ] 5.2 Implement data fetching logic
    - Create fetchDashboardData function
    - Call GET /kpis, /summary, /alerts endpoints in parallel
    - Update component state with responses
    - Add error handling with retry logic (max 3 retries)
    - Display user-friendly error messages
    - _Requirements: 1.1, 1.2, 20.2, 20.3, 20.4, 20.5_

  - [ ] 5.3 Implement auto-refresh functionality
    - Set up useEffect with setInterval for 30-second refresh
    - Clean up interval on component unmount
    - Update timestamp display on each refresh
    - _Requirements: 1.2, 1.3, 10.5_

  - [ ] 5.4 Create KPI status summary section
    - Display 3 cards showing counts of OK, WARNING, CRITICAL KPIs
    - Use green, yellow, red background colors
    - Display large count numbers
    - _Requirements: 2.4, 2.5, 2.6, 10.4_

  - [ ] 5.5 Create main metrics cards section
    - Display 4 cards: Documents, RFIs, Transmittals, Alerts
    - Show total count and breakdown for each
    - Use colored left border for visual distinction
    - _Requirements: 10.1, 10.2, 10.3_

  - [ ] 5.6 Create KPI cards grid
    - Map over kpis object to render KPICard components
    - Display in 2-column grid layout
    - Pass KPI data as props to KPICard
    - Add click handler to select KPI for historical view
    - _Requirements: 1.4, 1.5_

  - [ ] 5.7 Implement responsive layout
    - Use CSS Grid with responsive breakpoints
    - Adjust columns based on screen width (1 col mobile, 2 col tablet, 2-4 col desktop)
    - Ensure minimum font size of 12px
    - Support touch interactions
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

- [ ] 6. Create KPICard component
  - [ ] 6.1 Create KPICard component structure
    - Create `frontend/src/components/KPICard.tsx` file
    - Define KPICardProps interface
    - Accept kpiId, value, target, unit, status, variance, onClick props
    - _Requirements: 1.4_

  - [ ] 6.2 Implement status-based styling
    - Create getStatusColor helper function
    - Apply green border for OK status
    - Apply yellow border for WARNING status
    - Apply red border for CRITICAL status
    - _Requirements: 2.4, 2.5, 2.6_

  - [ ] 6.3 Implement value display
    - Display large value with unit
    - Show target value below
    - Display status badge in top-right corner
    - _Requirements: 1.4_

  - [ ] 6.4 Implement progress bar
    - Calculate progress percentage: (value / target) * 100
    - Display horizontal progress bar
    - Color bar based on status (green/yellow/red)
    - Cap progress at 100%
    - _Requirements: 1.5_

  - [ ] 6.5 Implement variance indicator
    - Display variance percentage
    - Show + or - prefix
    - Color green if positive, red if negative
    - _Requirements: 1.5_

- [ ] 7. Implement KPI historical chart
  - [ ] 7.1 Install Recharts library
    - Run npm install recharts in frontend directory





    - Add TypeScript types if needed
    - _Requirements: 11.1_

  - [x] 7.2 Create historical data fetching

    - Create fetchKpiHistory function

    - Call GET /kpi/{kpi_id}/history endpoint
    - Update kpiHistory state
    - Trigger fetch when selectedKpi changes
    - _Requirements: 11.1, 11.3_

  - [ ] 7.3 Implement LineChart component
    - Import LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend from recharts
    - Create ResponsiveContainer with 100% width and 300px height
    - Display 3 lines: average (blue), max (green), min (red)
    - Format X-axis with dates
    - Add tooltip for hover details
    - _Requirements: 11.1, 11.2_

  - [ ] 7.4 Add chart title and period selector
    - Display selected KPI ID as chart title
    - Show "7 Day Trend" subtitle
    - Add period selector buttons (7, 30, 90 days) for future enhancement
    - _Requirements: 11.3_

- [ ] 8. Implement alerts section
  - [ ] 8.1 Create alerts list display
    - Map over alerts array to render alert cards
    - Display alert type, KPI ID, message, timestamp
    - Color-code by type (red for critical, yellow for warning, blue for info)
    - Show only first 5 alerts with "View all" link
    - _Requirements: 12.3, 12.5_

  - [ ] 8.2 Implement alert acknowledgment
    - Add "Acknowledge" button to each alert
    - Call POST /alerts/{alert_id}/acknowledge on click
    - Remove alert from list after successful acknowledgment
    - Show success feedback
    - _Requirements: 13.1, 13.2, 13.3, 13.4_

  - [ ] 8.3 Add alert count badge
    - Display total unacknowledged alerts count
    - Show in main metrics section
    - Update count after acknowledgment
    - _Requirements: 10.3_

- [ ] 9. Add dashboard route to application
  - [ ] 9.1 Update App.tsx with dashboard route
    - Import Dashboard component
    - Add route `/projects/:projectId/dashboard`
    - Pass projectId from URL params to Dashboard component
    - _Requirements: 1.1_

  - [ ] 9.2 Add navigation link to dashboard
    - Update navigation menu to include Dashboard link
    - Add icon for dashboard (chart/graph icon)
    - Highlight active route
    - _Requirements: 1.1_

- [ ] 10. Implement data export functionality
  - [ ] 10.1 Create export API endpoint
    - Add GET /api/v1/projects/{project_id}/dashboard/export endpoint
    - Support format parameter (csv, json)
    - Support date_range parameter
    - Query KPIHistory for specified range
    - Generate CSV or JSON response
    - Set appropriate Content-Type and Content-Disposition headers
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5_

  - [ ] 10.2 Add export button to frontend
    - Add "Export Data" button to dashboard
    - Show dropdown for format selection (CSV, JSON)
    - Show date range picker
    - Trigger download on click
    - Show loading indicator during export
    - _Requirements: 18.1, 18.2, 18.4_

- [ ] 11. Add performance optimizations
  - [ ] 11.1 Implement database indexes
    - Verify indexes on kpi_metrics (project_id, kpi_id, recorded_at)
    - Verify indexes on kpi_history (project_id, kpi_id, recorded_at)
    - Verify indexes on dashboard_alerts (kpi_id, acknowledged, created_at)
    - _Requirements: 16.2_

  - [ ] 11.2 Implement API response caching
    - Add caching decorator to GET /kpis endpoint
    - Cache responses for 30 seconds
    - Use project_id and timestamp as cache key
    - _Requirements: 16.4_

  - [ ] 11.3 Optimize frontend rendering
    - Wrap KPICard component with React.memo
    - Use useMemo for expensive calculations
    - Implement loading skeletons for better perceived performance
    - _Requirements: 16.2, 16.3_

- [ ] 12. Add authentication and authorization
  - [ ] 12.1 Add authentication to dashboard endpoints
    - Add get_current_user dependency to all dashboard endpoints
    - Verify user is authenticated
    - Return 401 if not authenticated
    - _Requirements: 1.1_

  - [ ] 12.2 Add project access authorization
    - Create has_project_access helper function
    - Check if user has permission to view project
    - Return 403 if access denied
    - Apply to all dashboard endpoints
    - _Requirements: 19.1, 19.2_

  - [ ] 12.3 Add frontend authentication handling
    - Redirect to login if 401 response
    - Show "Access Denied" message if 403 response
    - Store authentication token in localStorage
    - Include token in API request headers
    - _Requirements: 1.1_

- [ ] 13. Create comprehensive documentation
  - [ ] 13.1 Write API documentation
    - Document all dashboard endpoints with OpenAPI/Swagger
    - Include request/response examples
    - Document error codes and messages
    - _Requirements: 14.4_

  - [ ] 13.2 Write user guide
    - Create user guide for dashboard usage
    - Include screenshots of dashboard sections
    - Explain KPI meanings and targets
    - Document how to acknowledge alerts
    - _Requirements: 1.1_

  - [ ] 13.3 Write ISO 9001:2015 compliance documentation
    - Document how dashboard supports ISO requirements
    - Create audit trail report template
    - Document data retention policies
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

---

## Implementation Notes

### Task Dependencies

- Tasks 1-2 (Models and Services) must be completed before Task 3 (API)
- Task 3 (API) must be completed before Task 4 (Background Tasks)
- Task 3 (API) must be completed before Task 5 (Frontend)
- Task 6 (KPICard) can be developed in parallel with Task 5
- Task 7 (Charts) depends on Task 5.6 (KPI selection)
- Task 8 (Alerts) depends on Task 5.2 (data fetching)

### Testing Strategy

- Write unit tests for each KPI calculation method in KPIService
- Write integration tests for dashboard API endpoints
- Write component tests for Dashboard and KPICard
- Test auto-refresh functionality
- Test error handling and retry logic
- Test responsive design on multiple screen sizes
- Performance test: Verify dashboard loads within 3 seconds
- Performance test: Verify KPI calculation completes within 30 seconds

### Implementation Priority

All tasks are required for a comprehensive implementation. The recommended implementation order is:

1. **Phase 1 (Backend Foundation)**: Tasks 1-2 (Models and Services)
2. **Phase 2 (API Layer)**: Task 3 (API Endpoints)
3. **Phase 3 (Automation)**: Task 4 (Background Tasks)
4. **Phase 4 (Frontend Core)**: Tasks 5-6 (Dashboard and KPICard)
5. **Phase 5 (Visualization)**: Tasks 7-8 (Charts and Alerts)
6. **Phase 6 (Integration)**: Task 9 (Routing)
7. **Phase 7 (Enhancement)**: Tasks 10-12 (Export, Performance, Auth)
8. **Phase 8 (Documentation)**: Task 13 (Comprehensive Docs)

---

**Document Control**
- Version: 1.0
- Date: 2025-11-03
- Status: Draft
- Based on: requirements.md v1.0, design.md v1.0
