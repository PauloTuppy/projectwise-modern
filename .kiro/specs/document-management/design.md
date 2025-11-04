# Document Management Subsystem - Design Document

## Overview

The Document Management Subsystem provides comprehensive file handling capabilities for the ProjectWise Modern platform. It enables users to upload documents up to 500MB, maintain version history with comments, control access through granular permissions, and automatically generate thumbnails for PDF files. The subsystem integrates with the existing FastAPI backend, PostgreSQL database, and AWS S3 storage infrastructure.

This design extends the existing document management foundation by adding:
- Enhanced permission management (View, Comment, Edit, Admin levels)
- Automatic thumbnail generation for PDFs
- Version commenting system
- Improved file size validation and upload progress tracking

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   API Layer     │  Next.js 14 API Routes (Edge Runtime)
│  (REST + WS)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  Service Layer  │  Business logic and orchestration
│                 │
│ - DocumentSvc   │  Core document operations
│ - PermissionSvc │  Access control management
│ - ThumbnailSvc  │  Async thumbnail generation (Cerebras AI)
│ - VersionSvc    │  Version management
└────────┬────────┘
         │
┌────────▼────────┐
│  Data Layer     │  Persistence and storage
│                 │
│ - Prisma ORM    │  Type-safe database access
│ - Vultr PostgreSQL │  Managed database
│ - Vultr Storage │  S3-compatible object storage
│ - Raindrop SmartSQL │  AI-enhanced queries
│ - Raindrop SmartBuckets │  RAG-enabled storage
└─────────────────┘
```

### Component Interaction Flow

**Upload Flow:**
```
Client → Next.js API Route → DocumentService → Vultr Storage
                                    ↓
                             VersionService → Prisma → PostgreSQL
                                    ↓
                             Raindrop SmartBuckets (RAG indexing)
                                    ↓
                             ThumbnailService (Cerebras AI) → Vultr Storage
```

**Permission Check Flow:**
```
Client → Next.js API Route → PermissionService → Raindrop SmartMemory (cache)
                                    ↓ (cache miss)
                             Prisma → PostgreSQL → Cache Update
```

## Components and Interfaces

### 1. Enhanced Document Service

**Purpose:** Orchestrates document operations including upload, retrieval, and validation

**Key Methods:**
```typescript
class DocumentService {
  async uploadDocument(
    projectId: string,
    file: File,
    userId: string,
    metadata: DocumentMetadata
  ): Promise<Document>
  
  async validateFileSize(file: File): Promise<boolean>
  
  async trackUploadProgress(
    uploadId: string,
    bytesUploaded: number,
    totalBytes: number
  ): Promise<void>
  
  async getDocumentWithPermissions(
    documentId: string,
    userId: string
  ): Promise<{ document: Document; permission: PermissionLevel }>
}
```

**Responsibilities:**
- File size validation (max 500MB)
- Upload progress tracking via WebSocket
- Document metadata extraction
- Integration with version and permission services

### 2. Permission Service (New)

**Purpose:** Manages document-level access control with four permission levels

**Permission Levels:**
- **View:** Read-only access to document content
- **Comment:** View + ability to add comments
- **Edit:** Comment + ability to create new versions
- **Admin:** Edit + ability to manage permissions

**Key Methods:**
```typescript
class PermissionService {
  async checkPermission(
    documentId: string,
    userId: string,
    requiredLevel: PermissionLevel
  ): Promise<boolean>
  
  async setPermission(
    documentId: string,
    userId: string,
    level: PermissionLevel,
    grantedBy: string
  ): Promise<DocumentPermission>
  
  async listDocumentPermissions(
    documentId: string
  ): Promise<DocumentPermission[]>
  
  async removePermission(
    documentId: string,
    userId: string
  ): Promise<void>
  
  async getCachedPermission(
    documentId: string,
    userId: string
  ): Promise<PermissionLevel | null>
}
```

**Caching Strategy:**
- Raindrop SmartMemory with key pattern: `perm:{document_id}:{user_id}`
- TTL: 300 seconds (5 minutes)
- Cache invalidation on permission updates

### 3. Version Service (Enhanced)

**Purpose:** Manages document versions with optional comments

**Key Methods:**
```typescript
class VersionService {
  async createVersion(
    documentId: string,
    file: File,
    userId: string,
    comment?: string
  ): Promise<DocumentVersion>
  
  async getVersionHistory(
    documentId: string,
    includeComments: boolean = true
  ): Promise<DocumentVersion[]>
  
  async getSpecificVersion(
    documentId: string,
    versionNumber: number
  ): Promise<DocumentVersion>
  
  async compareVersions(
    documentId: string,
    versionA: number,
    versionB: number
  ): Promise<VersionDiff>
}
```

**Version Numbering:**
- Sequential integers starting from 1
- Immutable once created
- Soft delete support (versions retained even if document deleted)

### 4. Thumbnail Service (New)

**Purpose:** Asynchronous generation of PDF thumbnails

**Key Methods:**
```typescript
class ThumbnailService {
  async generateThumbnail(
    documentId: string,
    filePath: string,
    pageNumber: number = 1
  ): Promise<string>  // Returns Vultr Storage URL
  
  async getThumbnailUrl(
    documentId: string
  ): Promise<string | null>
  
  async regenerateThumbnail(
    documentId: string
  ): Promise<string>
}
```

**Implementation Details:**
- Uses **Cerebras AI** for intelligent thumbnail generation (vision model)
- Generates 300px max dimension thumbnails
- Stores in Vultr Object Storage at: `thumbnails/{document_id}/thumb.jpg`
- Executed as background task via Next.js API route
- Graceful failure: logs error but doesn't block document upload

**Background Task (Next.js API Route):**
```typescript
// app/api/thumbnails/generate/route.ts
export async function POST(request: Request) {
  const { documentId, storagePath } = await request.json();
  
  try {
    // Download from Vultr Storage
    const file = await vultrStorage.download(storagePath);
    
    // Generate thumbnail using Cerebras AI vision
    const thumbnail = await cerebras.generateThumbnail(file, {
      maxDimension: 300,
      format: 'jpeg'
    });
    
    // Upload to Vultr Storage
    const thumbnailUrl = await vultrStorage.upload(
      `thumbnails/${documentId}/thumb.jpg`,
      thumbnail
    );
    
    // Update document metadata via Prisma
    await prisma.document.update({
      where: { id: documentId },
      data: { thumbnailUrl }
    });
    
    return Response.json({ success: true, thumbnailUrl });
  } catch (error) {
    console.error('Thumbnail generation failed:', error);
    return Response.json({ success: false, error: error.message }, { status: 500 });
  }
}
```

### 5. Storage Service (Enhanced)

**Purpose:** Handles file operations with S3

**Key Methods:**
```typescript
class StorageService {
  async uploadFile(
    file: File,
    storageKey: string,
    progressCallback?: (progress: number) => void
  ): Promise<string>  // Returns Vultr Storage URL
  
  async downloadFile(
    storageKey: string
  ): Promise<Buffer>
  
  async generatePresignedUrl(
    storageKey: string,
    expiration: number = 3600
  ): Promise<string>
  
  async deleteFile(storageKey: string): Promise<void>
  
  async getFileMetadata(
    storageKey: string
  ): Promise<Record<string, any>>
}
```

**Vultr Storage Key Structure:**
```
projects/{project_id}/documents/{document_id}/v{version_number}/{filename}
thumbnails/{document_id}/thumb.jpg
```

**Raindrop SmartBuckets Integration:**
- Automatic RAG indexing for document search
- Semantic search across all documents
- AI-powered metadata extraction

## Data Models

### Enhanced Document Model (Prisma Schema)

```prisma
enum FileType {
  PDF
  DWG
  DOCX
  XLSX
  TXT
  IMAGE
}

enum DocumentStatus {
  DRAFT
  REVIEW
  APPROVED
  ARCHIVED
}

model Document {
  id                String              @id @default(uuid())
  projectId         String
  name              String
  description       String?
  fileType          FileType            @default(PDF)
  discipline        String?
  status            DocumentStatus      @default(DRAFT)
  currentVersionId  String?
  ownerId           String
  thumbnailUrl      String?             // New field
  createdAt         DateTime            @default(now())
  updatedAt         DateTime            @updatedAt
  deletedAt         DateTime?           // Soft delete
  
  // Relationships
  project           Project             @relation(fields: [projectId], references: [id])
  owner             User                @relation(fields: [ownerId], references: [id])
  versions          DocumentVersion[]
  permissions       DocumentPermission[] // New
  comments          Comment[]
  metadata          DocumentMetadata?
  
  @@index([projectId, status, discipline])
  @@map("documents")
}
```

### Enhanced DocumentVersion Model (Prisma Schema)

```prisma
model DocumentVersion {
  id              String    @id @default(uuid())
  documentId      String
  versionNumber   Int
  filePath        String    // Vultr Storage URL
  fileSize        Int       // in bytes
  uploaderId      String
  comment         String?   // New field - version comment
  createdAt       DateTime  @default(now())
  
  // Relationships
  document        Document  @relation(fields: [documentId], references: [id], onDelete: Cascade)
  uploader        User      @relation(fields: [uploaderId], references: [id])
  
  @@unique([documentId, versionNumber])
  @@index([documentId, versionNumber])
  @@map("document_versions")
}
```

### DocumentPermission Model (New - Prisma Schema)

```prisma
enum PermissionLevel {
  VIEW
  COMMENT
  EDIT
  ADMIN
}

model DocumentPermission {
  id              String          @id @default(uuid())
  documentId      String
  userId          String
  permissionLevel PermissionLevel
  grantedBy       String
  grantedAt       DateTime        @default(now())
  
  // Relationships
  document        Document        @relation(fields: [documentId], references: [id], onDelete: Cascade)
  user            User            @relation("UserPermissions", fields: [userId], references: [id], onDelete: Cascade)
  granter         User            @relation("GrantedPermissions", fields: [grantedBy], references: [id])
  
  @@unique([documentId, userId])
  @@index([documentId])
  @@index([userId])
  @@map("document_permissions")
}
```

### DocumentMetadata Model (Enhanced - Prisma Schema)

```prisma
model DocumentMetadata {
  id                    String    @id @default(uuid())
  documentId            String    @unique
  fileHash              String    // SHA256 for deduplication
  mimeType              String
  pageCount             Int?      // For PDFs
  dimensions            Json?     // For CAD files
  thumbnailUrl          String?
  thumbnailGeneratedAt  DateTime?
  extractedText         String?   @db.Text // For OCR/search via Raindrop SmartBuckets
  
  // Relationships
  document              Document  @relation(fields: [documentId], references: [id], onDelete: Cascade)
  
  @@map("document_metadata")
}
```

## API Endpoints

### Document Upload
```
POST /api/v1/documents
Content-Type: multipart/form-data

Request Body:
- file: binary (max 500MB)
- project_id: UUID
- name: string (optional)
- description: string (optional)
- discipline: string (optional)

Response: 201 Created
{
  "id": "uuid",
  "name": "document.pdf",
  "file_type": "pdf",
  "current_version": 1,
  "thumbnail_url": null,  // Generated asynchronously
  "created_at": "2025-11-03T10:00:00Z"
}
```

### Get Document Versions
```
GET /api/v1/documents/{id}/versions

Response: 200 OK
{
  "document_id": "uuid",
  "versions": [
    {
      "version_number": 2,
      "comment": "Updated diagrams on page 3",
      "file_size": 2048576,
      "uploader": {
        "id": "uuid",
        "name": "John Doe"
      },
      "created_at": "2025-11-03T14:30:00Z"
    },
    {
      "version_number": 1,
      "comment": "Initial upload",
      "file_size": 1048576,
      "uploader": {
        "id": "uuid",
        "name": "Jane Smith"
      },
      "created_at": "2025-11-03T10:00:00Z"
    }
  ]
}
```

### Manage Permissions
```
PUT /api/v1/documents/{id}/permissions

Request Body:
{
  "user_id": "uuid",
  "permission_level": "edit"  // view | comment | edit | admin
}

Response: 200 OK
{
  "document_id": "uuid",
  "user_id": "uuid",
  "permission_level": "edit",
  "granted_at": "2025-11-03T15:00:00Z"
}
```

### List Document Permissions
```
GET /api/v1/documents/{id}/permissions

Response: 200 OK
{
  "document_id": "uuid",
  "permissions": [
    {
      "user": {
        "id": "uuid",
        "name": "John Doe",
        "email": "john@example.com"
      },
      "permission_level": "admin",
      "granted_by": "uuid",
      "granted_at": "2025-11-03T10:00:00Z"
    }
  ]
}
```

### Remove Permission
```
DELETE /api/v1/documents/{id}/permissions/{user_id}

Response: 204 No Content
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds maximum allowed size of 500MB",
    "details": {
      "file_size": 524288000,
      "max_size": 524288000
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| FILE_TOO_LARGE | 413 | File exceeds 500MB limit |
| INVALID_FILE_TYPE | 400 | Unsupported file type |
| PERMISSION_DENIED | 403 | User lacks required permission |
| DOCUMENT_NOT_FOUND | 404 | Document ID not found |
| VERSION_NOT_FOUND | 404 | Version number not found |
| THUMBNAIL_GENERATION_FAILED | 500 | Thumbnail creation error (non-blocking) |
| STORAGE_ERROR | 500 | S3 upload/download failure |
| DUPLICATE_PERMISSION | 409 | Permission already exists for user |

### Error Handling Strategy

1. **File Size Validation:** Check before upload starts, return 413 immediately
2. **Permission Checks:** Validate before any operation, cache results
3. **Thumbnail Failures:** Log error, continue without thumbnail, retry via Celery
4. **S3 Failures:** Retry 3 times with exponential backoff, then fail
5. **Database Errors:** Rollback transaction, return 500 with generic message

## Testing Strategy

### Unit Tests

**Document Service Tests:**
- `test_upload_document_success()` - Valid file upload
- `test_upload_document_exceeds_size_limit()` - 500MB+ file rejection
- `test_upload_document_invalid_type()` - Unsupported file type
- `test_get_document_with_permissions()` - Permission integration

**Permission Service Tests:**
- `test_check_permission_admin()` - Admin level access
- `test_check_permission_denied()` - Insufficient permission
- `test_set_permission_new_user()` - Grant new permission
- `test_set_permission_update_existing()` - Update existing permission
- `test_permission_cache_hit()` - Redis cache retrieval
- `test_permission_cache_invalidation()` - Cache update on change

**Version Service Tests:**
- `test_create_version_with_comment()` - Version with comment
- `test_create_version_without_comment()` - Version without comment
- `test_get_version_history()` - Chronological ordering
- `test_version_numbering_sequential()` - Correct version numbers

**Thumbnail Service Tests:**
- `test_generate_thumbnail_pdf()` - PDF thumbnail creation
- `test_generate_thumbnail_non_pdf()` - Graceful skip for non-PDFs
- `test_thumbnail_generation_failure()` - Error handling
- `test_thumbnail_dimensions()` - 300px max dimension

### Integration Tests

**Upload Flow Integration:**
- `test_upload_creates_version_and_permissions()` - End-to-end upload
- `test_upload_triggers_thumbnail_task()` - Async task queued
- `test_upload_progress_websocket()` - Progress updates sent

**Permission Flow Integration:**
- `test_permission_blocks_unauthorized_access()` - Access control
- `test_permission_allows_authorized_operations()` - Permitted operations
- `test_permission_inheritance_from_project()` - Project-level permissions

**Version Flow Integration:**
- `test_create_version_updates_current()` - Current version pointer
- `test_version_history_includes_comments()` - Comment retrieval
- `test_restore_version_creates_new()` - Version restoration

### API Tests

**Endpoint Tests:**
- `test_post_documents_valid()` - 201 response
- `test_post_documents_too_large()` - 413 response
- `test_get_versions_authenticated()` - 200 with versions
- `test_put_permissions_admin_only()` - 403 for non-admin
- `test_delete_permission_removes_access()` - Permission removal

### Performance Tests

**Load Tests:**
- Concurrent uploads: 50 simultaneous 100MB files
- Permission checks: 1000 requests/second
- Version history retrieval: <100ms for 50 versions
- Thumbnail generation: <5 seconds for 10-page PDF

**Stress Tests:**
- Maximum file size: 500MB upload completion
- Database connections: 100 concurrent permission checks
- Cache performance: Redis latency under load

## Security Considerations

1. **File Upload Security:**
   - Validate MIME type against file extension
   - Scan for malware using ClamAV (future enhancement)
   - Generate unique S3 keys to prevent overwrites

2. **Permission Security:**
   - Verify requester has Admin permission before granting permissions
   - Audit log all permission changes
   - Prevent permission escalation attacks

3. **Access Control:**
   - All API endpoints require authentication
   - Permission checks before every document operation
   - Presigned URLs expire after 1 hour

4. **Data Protection:**
   - S3 bucket encryption at rest (AES-256)
   - TLS 1.3 for data in transit
   - Soft delete prevents accidental data loss

## Performance Optimization

1. **Caching:**
   - Redis cache for permission lookups (5-minute TTL)
   - CDN for thumbnail delivery (future)
   - Database query result caching for version lists

2. **Async Operations:**
   - Thumbnail generation via Celery
   - Upload progress via WebSocket
   - Batch permission updates

3. **Database Optimization:**
   - Index on `document_permissions(document_id, user_id)`
   - Index on `document_versions(document_id, version_number)`
   - Composite index on `documents(project_id, status, discipline)`

4. **S3 Optimization:**
   - Multipart upload for files >100MB
   - S3 Transfer Acceleration for global users
   - Lifecycle policies for old versions

## Migration Plan

### Database Migrations (Prisma)

**Migration 1: Initial schema setup**
```bash
npx prisma migrate dev --name init_document_management
```

This will generate SQL migrations automatically from the Prisma schema for:
- Documents table with thumbnail_url field
- DocumentVersion table with comment field
- DocumentPermission table with all relationships
- DocumentMetadata table
- All indexes and constraints

**Migration 2: Backfill data (if needed)**
```typescript
// prisma/seed.ts
async function backfillPermissions() {
  const documents = await prisma.document.findMany({
    where: { permissions: { none: {} } }
  });
  
  for (const doc of documents) {
    await prisma.documentPermission.create({
      data: {
        documentId: doc.id,
        userId: doc.ownerId,
        permissionLevel: 'ADMIN',
        grantedBy: doc.ownerId
      }
    });
  }
}
```

### Deployment Steps (Raindrop Platform)

1. Update Prisma schema in `prisma/schema.prisma`
2. Generate Prisma client: `npx prisma generate`
3. Create migration: `npx prisma migrate dev`
4. Push to Git: `git push origin main`
5. **Raindrop auto-deploys** to global edge network
6. Run seed script if needed: `npx prisma db seed`
7. Monitor via Raindrop dashboard: `raindrop logs --follow`

**Zero-config deployment** - Raindrop handles:
- Database connection pooling
- Edge runtime optimization
- Auto-scaling
- Global distribution

## Future Enhancements

1. **Advanced Permissions:**
   - Time-limited access (expiring permissions)
   - Group-based permissions
   - Permission templates

2. **Enhanced Thumbnails:**
   - Multi-page thumbnails for PDFs
   - Video thumbnails for media files
   - 3D model previews for CAD files

3. **Version Comparison:**
   - Visual diff for PDFs
   - Text diff for documents
   - Annotation comparison

4. **Search:**
   - Full-text search using extracted text
   - Metadata-based filtering
   - Elasticsearch integration
