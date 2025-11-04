# ProjectWise Modern - Guia de Implementação das 7 Features
**Stack:** FastAPI (Backend) + React + Vite (Frontend)  
**Status:** Pronto para implementação ✅

---

## 📋 Checklist de Implementação

### Fase 1: Setup Inicial (✅ COMPLETO)
- [x] Criar .gitignore
- [x] Criar arquivos .env
- [x] Instalar dependências faltando
- [x] Corrigir erros de TypeScript
- [x] Build funcionando

### Fase 2: Features Core (🚧 PRÓXIMO)
- [ ] 1. Project Management (CRUD + Roles)
- [ ] 2. Document Upload + AI Analysis
- [ ] 3. Real-time Collaboration (WebSocket + Yjs)
- [ ] 4. Workflow Automation (RFIs + Transmittals)
- [ ] 5. Document Versioning
- [ ] 6. Dashboard com KPIs
- [ ] 7. Notifications System

---

## 🎯 Feature 1: Project Management (2-3 horas)

### Backend: Verificar Modelos Existentes
```bash
# Verificar se os modelos já existem
cat backend/app/models/project.py
```

**Modelos necessários:**
- ✅ Project (já existe)
- ✅ ProjectMember (já existe)

### Backend: Implementar Endpoints

**Arquivo:** `backend/app/api/v1/projects.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.project import Project, ProjectMember
from app.schemas.project import ProjectCreate, ProjectResponse, MemberInvite
import uuid

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user_id: str,
    db: Session = Depends(get_db)
):
    """Create new project"""
    new_project = Project(
        id=uuid.uuid4(),
        name=project.name,
        description=project.description,
        owner_id=current_user_id,
        status="active"
    )
    db.add(new_project)
    
    # Add creator as owner
    member = ProjectMember(
        id=uuid.uuid4(),
        project_id=new_project.id,
        user_id=current_user_id,
        role="owner"
    )
    db.add(member)
    db.commit()
    db.refresh(new_project)
    
    return new_project

@router.post("/{project_id}/invite")
async def invite_member(
    project_id: str,
    invite: MemberInvite,
    db: Session = Depends(get_db)
):
    """Invite member to project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create member
    member = ProjectMember(
        id=uuid.uuid4(),
        project_id=project_id,
        user_id=invite.user_id,
        role=invite.role
    )
    db.add(member)
    db.commit()
    
    return {"message": f"User invited as {invite.role}"}

@router.get("/{project_id}/members")
async def list_members(
    project_id: str,
    db: Session = Depends(get_db)
):
    """List all project members"""
    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    return {"members": members}
```

### Frontend: Componente de Gerenciamento

**Arquivo:** `frontend/src/components/ProjectManagement.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';

interface Member {
  id: string;
  user_id: string;
  role: 'owner' | 'manager' | 'editor' | 'viewer';
}

interface ProjectManagementProps {
  projectId: string;
}

export const ProjectManagement: React.FC<ProjectManagementProps> = ({ projectId }) => {
  const [members, setMembers] = useState<Member[]>([]);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<string>('editor');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMembers();
  }, [projectId]);

  const fetchMembers = async () => {
    try {
      const response = await axios.get(`/api/v1/projects/${projectId}/members`);
      setMembers(response.data.members);
    } catch (error) {
      console.error('Error fetching members:', error);
    }
  };

  const handleInviteMember = async () => {
    if (!inviteEmail) return;
    
    setLoading(true);
    try {
      await axios.post(`/api/v1/projects/${projectId}/invite`, {
        user_id: inviteEmail,
        role: inviteRole
      });
      
      setInviteEmail('');
      fetchMembers();
    } catch (error) {
      console.error('Error inviting member:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold">Project Management</h2>

      {/* Invite Member Section */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="font-bold mb-3">Invite Member</h3>
        <div className="flex gap-2">
          <input
            type="email"
            placeholder="Email"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            className="border p-2 rounded flex-1"
          />
          <select
            value={inviteRole}
            onChange={(e) => setInviteRole(e.target.value)}
            className="border p-2 rounded"
          >
            <option value="viewer">Viewer</option>
            <option value="editor">Editor</option>
            <option value="manager">Manager</option>
          </select>
          <Button onClick={handleInviteMember} disabled={loading}>
            {loading ? 'Inviting...' : 'Invite'}
          </Button>
        </div>
      </div>

      {/* Members List */}
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="font-bold mb-3">Team Members ({members.length})</h3>
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">User</th>
              <th className="text-left p-2">Role</th>
              <th className="text-left p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id} className="border-b">
                <td className="p-2">{member.user_id}</td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded text-sm ${
                    member.role === 'owner' ? 'bg-purple-100 text-purple-800' :
                    member.role === 'manager' ? 'bg-blue-100 text-blue-800' :
                    member.role === 'editor' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {member.role}
                  </span>
                </td>
                <td className="p-2">
                  {member.role !== 'owner' && (
                    <button className="text-red-500 text-sm">Remove</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

**Comandos para implementar:**
```bash
# 1. Verificar modelos existentes
cat backend/app/models/project.py

# 2. Atualizar rotas (se necessário)
# Editar backend/app/api/v1/projects.py

# 3. Criar componente React
# Criar frontend/src/components/ProjectManagement.tsx

# 4. Testar
cd backend
python -m uvicorn app.main:app --reload

cd frontend
npm run dev
```

---

## 🎯 Feature 2: Document Upload + AI Analysis (3-4 horas)

### Backend: Setup Gemini AI

**Instalar dependência:**
```bash
cd backend
pip install google-generativeai
pip freeze > requirements.txt
```

**Adicionar ao .env:**
```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

### Backend: Implementar Upload + Analysis

**Arquivo:** `backend/app/api/v1/documents.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
from app.database import get_db
from app.models.document import Document, DocumentAnalysis
from app.tasks.document_tasks import analyze_document_task
import google.generativeai as genai

router = APIRouter()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@router.post("/{project_id}/upload")
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload document with AI analysis"""
    
    # Validate file size (max 500MB)
    MAX_SIZE = 500 * 1024 * 1024  # 500MB
    file_content = await file.read()
    
    if len(file_content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 500MB)")
    
    # Save file
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create document record
    document = Document(
        id=uuid.uuid4(),
        project_id=project_id,
        name=file.filename,
        file_path=str(file_path),
        file_size=len(file_content),
        status="processing"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Trigger async AI analysis
    analyze_document_task.delay(str(document.id), str(file_path))
    
    return {
        "id": str(document.id),
        "name": file.filename,
        "status": "processing",
        "message": "Document uploaded. AI analysis in progress..."
    }

@router.get("/{document_id}/analysis")
async def get_analysis(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get AI analysis of document"""
    analysis = db.query(DocumentAnalysis).filter(
        DocumentAnalysis.document_id == document_id
    ).first()
    
    if not analysis:
        return {"status": "processing", "message": "Analysis in progress..."}
    
    return {
        "status": "complete",
        "summary": analysis.summary,
        "extracted_data": analysis.extracted_data,
        "ocr_text": analysis.ocr_text
    }
```

### Backend: Celery Task para AI Analysis

**Arquivo:** `backend/app/tasks/document_tasks.py`

```python
from celery import Celery
import os
import google.generativeai as genai
from app.database import SessionLocal
from app.models.document import Document, DocumentAnalysis
import uuid

celery_app = Celery(
    'projectwise',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@celery_app.task(bind=True, max_retries=3)
def analyze_document_task(self, document_id: str, file_path: str):
    """Analyze document with Gemini AI"""
    db = SessionLocal()
    
    try:
        # Read file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate summary
        summary_response = model.generate_content([
            {
                "mime_type": "application/pdf",
                "data": file_data
            },
            "Summarize this document in 3-5 sentences. Focus on key points and main topics."
        ])
        summary = summary_response.text
        
        # Extract data
        extract_response = model.generate_content([
            {
                "mime_type": "application/pdf",
                "data": file_data
            },
            "Extract key information, dates, numbers, and important data from this document. Format as bullet points."
        ])
        extracted = extract_response.text
        
        # OCR/Text extraction
        ocr_response = model.generate_content([
            {
                "mime_type": "application/pdf",
                "data": file_data
            },
            "Extract all text content from this document."
        ])
        ocr_text = ocr_response.text
        
        # Store analysis
        analysis = DocumentAnalysis(
            id=uuid.uuid4(),
            document_id=document_id,
            summary=summary,
            extracted_data=extracted,
            ocr_text=ocr_text
        )
        db.add(analysis)
        
        # Update document status
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "analyzed"
        
        db.commit()
        
        print(f"✅ Analysis complete for document {document_id}")
        
    except Exception as e:
        print(f"❌ Error analyzing document: {e}")
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()
```

### Frontend: Componente de Upload

**Arquivo:** `frontend/src/components/DocumentUpload.tsx`

```typescript
import React, { useState } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';

interface Analysis {
  status: string;
  summary?: string;
  extracted_data?: string;
  ocr_text?: string;
}

interface DocumentUploadProps {
  projectId: string;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ projectId }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Check file size (500MB max)
      const maxSize = 500 * 1024 * 1024;
      if (selectedFile.size > maxSize) {
        alert('File too large! Maximum size is 500MB');
        return;
      }
      
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `/api/v1/documents/${projectId}/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 1)
            );
            console.log(`Upload progress: ${percentCompleted}%`);
          }
        }
      );

      const docId = response.data.id;
      setDocumentId(docId);

      // Poll for analysis completion
      const pollInterval = setInterval(async () => {
        try {
          const result = await axios.get(`/api/v1/documents/${docId}/analysis`);
          
          if (result.data.status === 'complete') {
            setAnalysis(result.data);
            clearInterval(pollInterval);
            setUploading(false);
          }
        } catch (error) {
          console.error('Error checking analysis:', error);
        }
      }, 3000); // Check every 3 seconds

      // Stop polling after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setUploading(false);
      }, 300000);

    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
      setUploading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold">Upload Document</h2>

      {/* Upload Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Select Document (Max 500MB)
            </label>
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.txt"
              className="border p-2 rounded w-full"
              disabled={uploading}
            />
          </div>

          {file && (
            <div className="text-sm text-gray-600">
              Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </div>
          )}

          <Button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full"
          >
            {uploading ? 'Uploading & Analyzing...' : 'Upload & Analyze with AI'}
          </Button>
        </div>
      </div>

      {/* Analysis Results */}
      {analysis && analysis.status === 'complete' && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg shadow">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            <span className="mr-2">🤖</span>
            AI Analysis Results
          </h3>

          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">📝 Summary:</h4>
              <p className="text-gray-700 bg-white p-3 rounded">
                {analysis.summary}
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-2">🔍 Extracted Data:</h4>
              <div className="text-gray-700 bg-white p-3 rounded whitespace-pre-wrap">
                {analysis.extracted_data}
              </div>
            </div>

            {analysis.ocr_text && (
              <details className="cursor-pointer">
                <summary className="font-semibold mb-2">📄 Full Text Content</summary>
                <div className="text-gray-700 bg-white p-3 rounded mt-2 max-h-64 overflow-y-auto">
                  {analysis.ocr_text}
                </div>
              </details>
            )}
          </div>
        </div>
      )}

      {uploading && (
        <div className="bg-yellow-50 p-4 rounded-lg">
          <p className="text-center">
            ⏳ Analyzing document with AI... This may take a few moments.
          </p>
        </div>
      )}
    </div>
  );
};
```

---

## 🚀 Ordem de Implementação Recomendada

### Semana 1: Core Features
1. **Dia 1-2:** Feature 1 (Project Management)
2. **Dia 3-4:** Feature 2 (Document Upload + AI)
3. **Dia 5:** Feature 5 (Document Versioning)

### Semana 2: Collaboration & Workflows
4. **Dia 1-2:** Feature 3 (Real-time Collaboration)
5. **Dia 3-4:** Feature 4 (Workflow Automation)

### Semana 3: Polish & Deploy
6. **Dia 1:** Feature 6 (Dashboard)
7. **Dia 2:** Feature 7 (Notifications)
8. **Dia 3-5:** Testing, Bug Fixes, Deploy

---

## 📝 Próximos Passos Imediatos

1. **Implementar Feature 1 (Project Management)**
   ```bash
   # Verificar modelos existentes
   cat backend/app/models/project.py
   
   # Criar componente React
   # Copiar código do ProjectManagement.tsx acima
   ```

2. **Testar Feature 1**
   ```bash
   # Backend
   cd backend
   python -m uvicorn app.main:app --reload
   
   # Frontend (novo terminal)
   cd frontend
   npm run dev
   ```

3. **Implementar Feature 2 (Document Upload + AI)**
   ```bash
   # Instalar Gemini
   pip install google-generativeai
   
   # Configurar .env com GEMINI_API_KEY
   # Implementar endpoints e componentes
   ```

---

## 🎯 Quer começar agora?

Escolha uma opção:

**A)** Implementar Feature 1 (Project Management) - Mais simples, sem dependências externas

**B)** Implementar Feature 2 (Document Upload + AI) - Mais impressionante, requer Gemini API

**C)** Ver código completo de outra feature específica

Me avise qual você quer começar e eu te guio passo a passo! 🚀
