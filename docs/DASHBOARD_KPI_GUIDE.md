# Dashboard com KPIs - ISO 9001:2015 Compliant

## Overview
Dashboard executivo com métricas de qualidade em tempo real seguindo os requisitos da ISO 9001:2015.

## KPIs Definidos

| KPI ID | Nome | Métrica | Target | Frequência |
|--------|------|---------|--------|-----------|
| KPI-001 | Taxa Sucesso Upload | Uploads OK / Total | >= 99.5% | Real-time |
| KPI-002 | Tempo Análise IA | Segundos (P50) | <= 30s | Real-time |
| KPI-003 | Acurácia IA | Confidence Score | >= 90% | Diário |
| KPI-004 | RFI Response Time | Dias média | <= 3 dias | Diário |
| KPI-005 | RFI Closure Rate | % fechadas | >= 95% | Semanal |
| KPI-006 | Transmittal Approval | Dias média | <= 5 dias | Diário |
| KPI-007 | On-time Completion | % no prazo | >= 90% | Semanal |

## Implementação

### Backend
- `backend/app/models/kpi.py` - Modelos de dados
- `backend/app/services/kpi_service.py` - Cálculo de KPIs
- `backend/app/api/dashboard.py` - API endpoints
- `backend/app/tasks/kpi_tasks.py` - Tarefas agendadas

### Frontend
- `frontend/src/components/Dashboard.tsx` - Componente principal
- `frontend/src/components/KPICard.tsx` - Card de KPI

## API Endpoints

### GET /api/v1/projects/{project_id}/dashboard/kpis
Retorna todos os KPIs do projeto

### GET /api/v1/projects/{project_id}/dashboard/summary
Retorna resumo do dashboard

### GET /api/v1/projects/{project_id}/dashboard/kpi/{kpi_id}/history
Retorna histórico de um KPI

### GET /api/v1/projects/{project_id}/dashboard/alerts
Retorna alertas ativos

### POST /api/v1/projects/{project_id}/dashboard/alerts/{alert_id}/acknowledge
Reconhece um alerta

## Conformidade ISO 9001:2015

| Requisito | Implementação | Status |
|---|---|---|
| 4.4.1 QMS Processes | KPI tracking | ✓ |
| 7.1.5 Monitoring | Real-time metrics | ✓ |
| 9.1.1 Performance | KPI metrics | ✓ |
| 9.2.1 Audit | Historical data | ✓ |
| 10.2.1 Nonconformity | Alert system | ✓ |

## Setup

1. Criar tabelas no banco:
```bash
cd backend
alembic revision --autogenerate -m "Add KPI tables"
alembic upgrade head
```

2. Instalar dependências frontend:
```bash
cd frontend
npm install recharts
```

3. Configurar Celery Beat no backend/app/main.py

4. Acessar dashboard em: `/projects/{projectId}/dashboard`
