from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.project import Project, ProjectMember, ProjectStatusEnum
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectMemberResponse
from app.services.project_service import ProjectService
from app.security import get_current_user, verify_project_access

router = APIRouter()
project_service = ProjectService()

# CREATE Project
 @router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    new_project = project_service.create_project(
        db=db,
        owner_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        disciplines=project_data.disciplines
    )
    return new_project

# READ Projects
 @router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all projects for current user"""
    projects = project_service.list_user_projects(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return projects

# READ Single Project
 @router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project by ID"""
    project = verify_project_access(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# UPDATE Project
 @router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project (owner only)"""
    project = verify_project_access(db, project_id, current_user.id, require_owner=True)
    if not project:
        raise HTTPException(status_code=403, detail="Only project owner can update")
    
    updated = project_service.update_project(db, project, project_data)
    return updated

# DELETE Project
 @router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project (owner only)"""
    project = verify_project_access(db, project_id, current_user.id, require_owner=True)
    if not project:
        raise HTTPException(status_code=403, detail="Only project owner can delete")
    
    project_service.delete_project(db, project)
    return {"message": "Project deleted successfully"}

# ADD Member to Project
 @router.post("/projects/{project_id}/members")
async def add_project_member(
    project_id: str,
    member_email: str,
    role: str = "editor",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add member to project"""
    project = verify_project_access(db, project_id, current_user.id, require_owner=True)
    if not project:
        raise HTTPException(status_code=403, detail="Only project owner can add members")
    
    member = project_service.add_member(db, project_id, member_email, role)
    return {"message": "Member added", "member": member}

# LIST Project Members
 @router.get("/projects/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all members in project"""
    project = verify_project_access(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    members = project_service.list_members(db, project_id)
    return members

# REMOVE Member from Project
 @router.delete("/projects/{project_id}/members/{user_id}")
async def remove_project_member(
    project_id: str,
    user_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from project (owner only)"""
    project = verify_project_access(db, project_id, current_user.id, require_owner=True)
    if not project:
        raise HTTPException(status_code=403, detail="Only project owner can remove members")
    
    project_service.remove_member(db, project_id, user_id)
    return {"message": "Member removed"}