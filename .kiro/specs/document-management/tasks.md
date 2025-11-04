# Implementation Plan

- [ ] 1. Create Prisma schema and migrations for permission system
  - [ ] 1.1 Define DocumentPermission model in Prisma schema
    - Add DocumentPermission model in `prisma/schema.prisma` with fields: id, documentId, userId, permissionLevel, grantedBy, grantedAt
    - Define PermissionLevel enum with values: VIEW, COMMENT, EDIT, ADMIN
    - Add unique constraint on (documentId, userId)
    - Add relationships to Document and User models
    - _Requirements: 3.1, 3.2, 3.6_
  
  - [ ] 1.2 Add thumbnail_url and comment fields to existing Prisma models
    - Add `thumbnailUrl` field to Document model
    - Add `comment` field to DocumentVersion model
    - Update model relationships
    - _Requirements: 2.2, 4.2_
  
  - [ ] 1.3 Generate and run Prisma migrations
    - Run `npx prisma migrate dev --name add_permissions_and_thumbnails`
    - Generate Prisma client: `npx prisma generate`
    - Verify migration in database
    - _Requirements: 3.1, 2.2, 4.2_

- [ ] 2. Implement Permission Service with Raindrop SmartMemory caching
  - [ ] 2.1 Create PermissionService class with core methods
    - Create `lib/services/permission-service.ts` with TypeScript class
    - Implement `checkPermission()` method with permission level hierarchy
    - Implement `setPermission()` method with admin validation
    - Implement `listDocumentPermissions()` method
    - Implement `removePermission()` method
    - Add permission level comparison logic (Admin > Edit > Comment > View)
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  
  - [ ] 2.2 Add Raindrop SmartMemory caching layer for permissions
    - Implement `getCachedPermission()` method using Raindrop SmartMemory
    - Implement cache invalidation on permission updates
    - Set TTL to 300 seconds (5 minutes)
    - Use key pattern: `perm:{documentId}:{userId}`
    - _Requirements: 3.7_
  
  - [ ] 2.3 Create TypeScript types for permission requests/responses
    - Create types in `types/permission.ts`
    - Define PermissionCreate, PermissionUpdate, PermissionResponse types
    - Add Zod schemas for validation
    - _Requirements: 3.2, 5.3, 5.4_

- [ ] 3. Enhance Document Service with file size validation
  - [ ] 3.1 Add file size validation method
    - Create `lib/services/document-service.ts` with TypeScript class
    - Implement `validateFileSize()` method checking 500MB limit
    - Return descriptive error for oversized files
    - Add MAX_FILE_SIZE constant to environment config
    - _Requirements: 1.1, 1.2, 5.4_
  
  - [ ] 3.2 Integrate permission checks into document operations
    - Add permission validation before document retrieval
    - Add permission validation before version creation
    - Add permission validation before permission management
    - Use PermissionService.checkPermission() in all operations
    - _Requirements: 3.7_
  
  - [ ] 3.3 Add upload progress tracking via Socket.io
    - Implement `trackUploadProgress()` method
    - Emit progress events to Socket.io connection
    - Calculate percentage based on bytes uploaded
    - Create WebSocket handler in `app/api/socket/route.ts`
    - _Requirements: 1.4_

- [ ] 4. Implement Version Service with comments
  - [ ] 4.1 Create VersionService class
    - Create `lib/services/version-service.ts` with TypeScript class
    - Implement `createVersion()` method accepting optional comment parameter
    - Implement `getVersionHistory()` method with comment inclusion
    - Implement `getSpecificVersion()` method
    - Ensure sequential version numbering using Prisma transactions
    - Update document's currentVersionId pointer
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  
  - [ ] 4.2 Update existing document upload to use VersionService
    - Refactor DocumentService.uploadDocument() to use VersionService
    - Pass "Initial upload" as default comment for first version
    - Use Prisma client for database operations
    - _Requirements: 2.1, 2.2_

- [ ] 5. Implement Thumbnail Service with Cerebras AI
  - [ ] 5.1 Create ThumbnailService class with Cerebras AI integration
    - Create `lib/services/thumbnail-service.ts` with TypeScript class
    - Implement `generateThumbnail()` method using Cerebras vision model
    - Set maximum dimension to 300 pixels
    - Upload generated thumbnail to Vultr Storage at `thumbnails/{documentId}/thumb.jpg`
    - Return Vultr Storage URL of thumbnail
    - Handle non-PDF files gracefully (skip thumbnail generation)
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  
  - [ ] 5.2 Create Next.js API route for async thumbnail generation
    - Create `app/api/thumbnails/generate/route.ts` endpoint
    - Accept documentId and storagePath in request body
    - Download file from Vultr Storage, generate thumbnail with Cerebras
    - Upload thumbnail to Vultr Storage
    - Update document.thumbnailUrl via Prisma
    - Log errors without blocking document upload
    - _Requirements: 4.1, 4.3_
  
  - [ ] 5.3 Integrate thumbnail generation into document upload flow
    - Trigger thumbnail API call after successful document upload
    - Only trigger for PDF file types
    - Pass documentId and Vultr Storage path
    - Use fetch() to call thumbnail endpoint asynchronously
    - _Requirements: 4.1_

- [ ] 6. Create Next.js API routes for permission management
  - [ ] 6.1 Implement PUT /api/documents/[id]/permissions route
    - Create `app/api/documents/[id]/permissions/route.ts` with PUT handler
    - Validate requester has Admin permission using WorkOS auth
    - Accept userId and permissionLevel in request body with Zod validation
    - Call PermissionService.setPermission()
    - Return 200 with permission details or 403 if unauthorized
    - _Requirements: 3.2, 5.3, 5.4, 5.5_
  
  - [ ] 6.2 Implement GET /api/documents/[id]/permissions route
    - Add GET handler in same route file
    - Validate requester has at least View permission
    - Call PermissionService.listDocumentPermissions()
    - Return 200 with permissions array including user details from Prisma
    - _Requirements: 3.7, 5.3, 5.5_
  
  - [ ] 6.3 Implement DELETE /api/documents/[id]/permissions/[userId] route
    - Create `app/api/documents/[id]/permissions/[userId]/route.ts` with DELETE handler
    - Validate requester has Admin permission
    - Call PermissionService.removePermission()
    - Return 204 on success or 403 if unauthorized
    - _Requirements: 3.2, 5.4_

- [ ] 7. Enhance existing document API routes with new features
  - [ ] 7.1 Update POST /api/documents route
    - Create or update `app/api/documents/route.ts` with POST handler
    - Add file size validation before upload using DocumentService
    - Return 413 error if file exceeds 500MB
    - Upload to Vultr Object Storage using Raindrop SmartBuckets
    - Include thumbnailUrl (null initially) in response
    - Trigger thumbnail generation API call for PDFs
    - _Requirements: 1.1, 1.2, 1.3, 4.1, 5.1, 5.5_
  
  - [ ] 7.2 Create GET /api/documents/[id]/versions route
    - Create `app/api/documents/[id]/versions/route.ts` with GET handler
    - Validate requester has at least View permission
    - Call VersionService.getVersionHistory()
    - Return versions in reverse chronological order with comments
    - Include uploader details from Prisma relations
    - _Requirements: 2.3, 2.5, 5.2, 5.5_
  
  - [ ] 7.3 Update existing document retrieval route
    - Create or update `app/api/documents/[id]/route.ts` with GET handler
    - Add permission checks using PermissionService
    - Include thumbnailUrl in document response
    - Include current permission level for requesting user
    - Return 403 if user lacks View permission
    - _Requirements: 3.7, 4.4_

- [ ] 8. Add error handling and validation
  - [ ] 8.1 Create custom error classes
    - Create `lib/errors/document-errors.ts` with custom Error classes
    - Define FileTooLargeError (413)
    - Define PermissionDeniedError (403)
    - Define DocumentNotFoundError (404)
    - Define VersionNotFoundError (404)
    - Export error types and HTTP status codes
    - _Requirements: 5.4_
  
  - [ ] 8.2 Implement error response formatting
    - Create `lib/utils/error-handler.ts` utility
    - Create error response type with code, message, details
    - Map errors to error codes (FILE_TOO_LARGE, PERMISSION_DENIED, etc.)
    - Include relevant details in error responses
    - Use in all API route handlers with try-catch blocks
    - _Requirements: 5.4_

- [ ] 9. Set up default permissions on document creation
  - [ ] 9.1 Auto-grant Admin permission to document creator
    - Modify DocumentService.uploadDocument() to create permission record
    - Use Prisma transaction to create document and permission atomically
    - Set permissionLevel to ADMIN for ownerId
    - Set grantedBy to ownerId (self-granted)
    - _Requirements: 3.1_

- [ ] 10. Add database indexes for performance
  - [ ] 10.1 Add indexes in Prisma schema
    - Add @@index([documentId]) to DocumentPermission model
    - Add @@index([userId]) to DocumentPermission model
    - Add @@index([projectId, status, discipline]) to Document model
    - Add @@index([documentId, versionNumber]) to DocumentVersion model
    - Run `npx prisma migrate dev` to apply indexes
    - _Requirements: Performance optimization_

- [ ]* 11. Write integration tests for permission flows
  - [ ]* 11.1 Test permission-based access control
    - Create test file `__tests__/integration/permissions.test.ts`
    - Test unauthorized access returns 403
    - Test View permission allows read-only
    - Test Edit permission allows version creation
    - Test Admin permission allows permission management
    - Use Vitest or Jest with Prisma test database
    - _Requirements: 3.3, 3.4, 3.5, 3.6_
  
  - [ ]* 11.2 Test permission caching behavior
    - Test cache hit returns cached permission from Raindrop SmartMemory
    - Test cache miss queries Prisma database
    - Test cache invalidation on permission update
    - _Requirements: 3.7_

- [ ]* 12. Write integration tests for version management
  - [ ]* 12.1 Test version creation with comments
    - Create test file `__tests__/integration/versions.test.ts`
    - Test version with comment is stored correctly in Prisma
    - Test version without comment uses null
    - Test version numbering is sequential
    - Test currentVersionId is updated
    - _Requirements: 2.1, 2.2, 2.4, 2.5_
  
  - [ ]* 12.2 Test version history retrieval
    - Test versions returned in chronological order
    - Test comments included in response
    - Test uploader details populated from Prisma relations
    - _Requirements: 2.3, 2.5_

- [ ]* 13. Write integration tests for thumbnail generation
  - [ ]* 13.1 Test thumbnail API execution
    - Create test file `__tests__/integration/thumbnails.test.ts`
    - Test PDF upload triggers thumbnail API call
    - Test non-PDF upload skips thumbnail generation
    - Test thumbnail uploaded to correct Vultr Storage path
    - Test document.thumbnailUrl updated after generation via Prisma
    - Mock Cerebras AI responses
    - _Requirements: 4.1, 4.2_
  
  - [ ]* 13.2 Test thumbnail failure handling
    - Test thumbnail failure logs error
    - Test thumbnail failure doesn't block upload
    - Test graceful degradation when Cerebras unavailable
    - _Requirements: 4.3_

- [ ]* 14. Write API route tests
  - [ ]* 14.1 Test permission management routes
    - Create test file `__tests__/api/permissions.test.ts`
    - Test PUT /api/documents/[id]/permissions with valid admin
    - Test PUT returns 403 for non-admin users
    - Test GET /api/documents/[id]/permissions returns all permissions
    - Test DELETE removes permission successfully
    - Mock WorkOS authentication
    - _Requirements: 5.3, 5.4, 5.5_
  
  - [ ]* 14.2 Test enhanced document routes
    - Create test file `__tests__/api/documents.test.ts`
    - Test POST /api/documents rejects files over 500MB
    - Test GET /api/documents/[id]/versions returns version history
    - Test document responses include thumbnailUrl
    - Mock Vultr Storage and Raindrop SmartBuckets
    - _Requirements: 1.1, 1.2, 5.1, 5.2, 5.5_
