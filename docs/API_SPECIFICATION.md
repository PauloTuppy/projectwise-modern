# ProjectWise Modern - Especificação Completa para Kiro

## 1. Visão Geral do Sistema

**Nome do Projeto**: ProjectWise Modern
**Versão**: 1.0
**Status**: Concept → MVP
**Objetivo**: Reimaginar o ProjectWise como uma plataforma web moderna de colaboração em tempo real para projetos de engenharia e construção

---

## 2. User Stories & Personas

### Persona 1: Project Manager (PM)
- **Objetivo**: Coordenar equipes, acompanhar progresso, gerenciar aprovações
- **User Stories**:
  - Como PM, quero criar projetos e adicionar membros da equipe
  - Como PM, quero visualizar dashboards de KPI em tempo real
  - Como PM, quero configurar workflows de aprovação personalizados

### Persona 2: Engineer
- **Objetivo**: Colaborar em documentos, compartilhar designs, receber feedback
- **User Stories**:
  - Como engenheiro, quero fazer upload de arquivos DWG/PDF
  - Como engenheiro, quero editar documentos colaborativamente
  - Como engenheiro, quero receber comentários de colegas em tempo real

### Persona 3: Validator/Lead
- **Objetivo**: Revisar, validar e aprovar documentos
- **User Stories**:
  - Como líder, quero criar RFIs (Requests for Information)
  - Como líder, quero revisar versões anteriores
  - Como líder, quero aprovar ou rejeitar transmittals

---

## 3. Core Subsystems

### 3.1 Authentication & Authorization

**Subsystem**: User Management & Security

**Requirements**:
- OAuth2 com Supabase ou Firebase Auth
- Roles: Admin, Manager, Engineer, Viewer
- RBAC (Role-Based Access Control)
- Audit logging de ações do usuário
- Suporte a 2FA

**API Endpoints**:
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me (current user)
PUT    /api/v1/auth/profile
POST   /api/v1/auth/verify-2fa
```

**Data Models**:
```
User:
  - id: UUID
  - email: string
  - name: string
  - role: enum[Admin, Manager, Engineer, Viewer]
  - avatar_url: string
  - created_at: timestamp
  - updated_at: timestamp
```

---

### 3.2 Project Management

**Subsystem**: Projects & Workspaces

**Requirements**:
- Criar projetos com nome, descrição, disciplinas
- Adicionar/remover membros com permissões específicas
- Arquivar projetos
- Exportar relatórios de projeto

**API Endpoints**:
```
POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/{project_id}
PUT    /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
POST   /api/v1/projects/{project_id}/members
GET    /api/v1/projects/{project_id}/members
DELETE /api/v1/projects/{project_id}/members/{user_id}
```

**Data Models**:
```
Project:
  - id: UUID
  - name: string
  - description: string
  - owner_id: UUID (FK User)
  - disciplines: array[string] (e.g., ["Arquitetura", "Estrutura", "MEP"])
  - status: enum[Active, Archived, Completed]
  - created_at: timestamp
  - updated_at: timestamp

ProjectMember:
  - id: UUID
  - project_id: UUID (FK Project)
  - user_id: UUID (FK User)
  - role: enum[Owner, Manager, Editor, Viewer]
  - permissions: JSON (custom permissions)
```

---

### 3.3 Document Management

**Subsystem**: Upload, Versionamento e Armazenamento

**Requirements**:
- Upload de arquivos (máx 500MB por arquivo)
- Suporte para: PDF, DWG, DOCX, XLSX, TXT, Images
- Versionamento automático com histórico completo
- Metadata extraction (autor, data, dimensões)
- Soft delete com recovery
- Thumbnail generation para PDFs/Images

**API Endpoints**:
```
POST   /api/v1/projects/{project_id}/documents
GET    /api/v1/projects/{project_id}/documents
GET    /api/v1/documents/{document_id}
PUT    /api/v1/documents/{document_id}
DELETE /api/v1/documents/{document_id}
GET    /api/v1/documents/{document_id}/versions
GET    /api/v1/documents/{document_id}/versions/{version_id}
POST   /api/v1/documents/{document_id}/restore/{version_id}
GET    /api/v1/documents/{document_id}/download
```

**Data Models**:
```
Document:
  - id: UUID
  - project_id: UUID (FK Project)
  - name: string
  - description: string
  - file_type: enum[pdf, dwg, docx, xlsx, txt, image]
  - discipline: string
  - status: enum[Draft, Review, Approved, Archived]
  - current_version_id: UUID
  - owner_id: UUID (FK User)
  - created_at: timestamp
  - updated_at: timestamp
  - deleted_at: timestamp (soft delete)

DocumentVersion:
  - id: UUID
  - document_id: UUID (FK Document)
  - version_number: integer
  - file_path: string (S3/Storage URL)
  - file_size: integer
  - uploader_id: UUID (FK User)
  - change_summary: string
  - created_at: timestamp

DocumentMetadata:
  - id: UUID
  - document_id: UUID
  - file_hash: string (SHA256)
  - dimensions: JSON (para CAD files)
  - page_count: integer (para PDFs)
  - thumbnail_url: string
  - extracted_text: text (para OCR)
```

---

### 3.4 Real-time Collaboration

**Subsystem**: Edição Colaborativa & Presença

**Requirements**:
- Edição simultânea de documentos (CRDT-based)
- Presença de usuários em tempo real (cursor positions, selections)
- Comments/Markup inline
- Conflict resolution automática
- Change tracking
- Undo/Redo com histórico compartilhado

**WebSocket Events**:
```
document:opened
document:closed
document:changed (delta-based)
document:comment:added
document:comment:updated
document:comment:resolved
user:present
user:cursor
user:selection
```

**Data Models**:
```
DocumentSession:
  - id: UUID
  - document_id: UUID
  - user_id: UUID
  - cursor_position: integer
  - selection_range: {start, end}
  - opened_at: timestamp
  - last_activity: timestamp

Comment:
  - id: UUID
  - document_id: UUID (FK Document)
  - author_id: UUID (FK User)
  - position: integer (character offset ou page/line)
  - text: string
  - resolved: boolean
  - created_at: timestamp
  - resolved_at: timestamp
  - replies: array[Comment]
```

---

### 3.5 Workflow & Approvals

**Subsystem**: RFIs, Transmittals, Aprovações

**Requirements**:
- Criar RFIs (Request for Information)
- Criar Transmittals com múltiplos documentos
- Workflows de aprovação em cadeia
- SLAs e vencimentos
- Notificações automáticas
- Histórico completo de mudanças de status

**API Endpoints**:
```
POST   /api/v1/projects/{project_id}/rfis
GET    /api/v1/projects/{project_id}/rfis
GET    /api/v1/rfis/{rfi_id}
PUT    /api/v1/rfis/{rfi_id}
POST   /api/v1/rfis/{rfi_id}/answer

POST   /api/v1/projects/{project_id}/transmittals
GET    /api/v1/projects/{project_id}/transmittals
GET    /api/v1/transmittals/{transmittal_id}
POST   /api/v1/transmittals/{transmittal_id}/approve
POST   /api/v1/transmittals/{transmittal_id}/reject
```

**Data Models**:
```
RFI:
  - id: UUID
  - project_id: UUID
  - created_by: UUID (FK User)
  - assigned_to: UUID (FK User)
  - title: string
  - description: string
  - status: enum[Open, Answered, Closed]
  - priority: enum[Low, Medium, High, Critical]
  - due_date: timestamp
  - created_at: timestamp

Transmittal:
  - id: UUID
  - project_id: UUID
  - created_by: UUID
  - document_ids: array[UUID]
  - status: enum[Draft, Submitted, Approved, Rejected, Superseded]
  - approval_chain: array[{user_id, status, timestamp, comments}]
  - created_at: timestamp

WorkflowTemplate:
  - id: UUID
  - project_id: UUID
  - name: string
  - approvers: array[UUID] (ordered)
  - auto_notify: boolean
  - requires_all_approval: boolean
```

---

### 3.6 Notifications & Alerts

**Subsystem**: Notificações em Tempo Real

**Requirements**:
- In-app notifications
- Email notifications (customizable)
- Notification preferences por usuário
- Bulk notifications para workflows
- Read/Unread tracking

**API Endpoints**:
```
GET    /api/v1/notifications
GET    /api/v1/notifications?unread=true
POST   /api/v1/notifications/{notification_id}/read
POST   /api/v1/notifications/mark-all-read
GET    /api/v1/notification-preferences
PUT    /api/v1/notification-preferences
```

---

### 3.7 Dashboards & Reporting

**Subsystem**: KPIs e Visualizações

**Requirements**:
- Real-time KPI dashboard
- Métricas: documentos por status, RFIs abertos, upload velocity
- Relatórios exportáveis (PDF/Excel)
- Gráficos de progresso temporal
- Filtros por disciplina, status, usuário

**API Endpoints**:
```
GET    /api/v1/projects/{project_id}/dashboard/kpis
GET    /api/v1/projects/{project_id}/reports/documents
GET    /api/v1/projects/{project_id}/reports/workflow
GET    /api/v1/projects/{project_id}/reports/export/{format}
```

**Métricas**:
```
KPI:
  - total_documents
  - documents_by_status: {Draft, Review, Approved, Archived}
  - documents_by_discipline
  - open_rfis
  - overdue_rfis
  - pending_approvals
  - upload_velocity (docs/day)
  - avg_approval_time
  - active_collaborators
```

---

## 4. Technical Architecture

### 4.1 Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ com Supabase
- **Real-time**: WebSockets (FastAPI native)
- **CRDT**: Yjs (via Python bindings)
- **Cache**: Redis
- **Storage**: AWS S3 ou Google Cloud Storage
- **Message Queue**: Celery com Redis

### 4.2 Frontend Stack
- **Framework**: React 18 + TypeScript
- **State**: Zustand ou TanStack Query
- **Real-time**: Socket.IO ou native WebSockets
- **CRDT**: Yjs
- **Rich Editor**: ProseMirror ou Tiptap
- **Styling**: Tailwind CSS

### 4.3 DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose (local), Kubernetes (prod)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

---

## 5. Security Requirements

1. **Authentication**: OAuth2 + JWT
2. **Encryption**: TLS 1.3, AES-256 para dados sensíveis
3. **Rate Limiting**: 100 req/min por IP
4. **CORS**: Configurar domínios específicos
5. **CSRF**: Token validation
6. **SQL Injection Prevention**: Prepared statements (SQLAlchemy ORM)
7. **XSS Prevention**: Content Security Policy headers
8. **Audit Logging**: Todas ações de usuário registradas

---

## 6. Performance & Scalability

- **API Response Time**: < 200ms (p95)
- **WebSocket Latency**: < 50ms (p95)
- **Concurrent Users**: 1000+ simultâneos (per instance)
- **Document Size Limit**: 500MB
- **Storage**: Escalável via S3
- **Database**: Connection pooling, query optimization

---

## 7. Phased Rollout

### MVP (Sprint 1-2):
- [ ] Auth & basic RBAC
- [ ] Project creation & members
- [ ] Document upload & versioning
- [ ] Basic dashboard

### Phase 2 (Sprint 3-4):
- [ ] Real-time collaboration
- [ ] Comments/Markup
- [ ] RFI/Transmittal workflows
- [ ] Email notifications

### Phase 3 (Sprint 5-6):
- [ ] Advanced reporting
- [ ] MCP integrations
- [ ] Performance optimization
- [ ] Mobile support

---

## 8. Success Criteria

- [x] Spec-driven development completo
- [ ] Zero downtime deployments
- [ ] 99.9% uptime
- [ ] Sub-second real-time sync
- [ ] 90%+ user adoption na org-pilot
- [ ] < 5s page load time projectwise-spec