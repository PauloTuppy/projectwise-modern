from sqlalchemy.orm import Session
import uuid

from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    def create_project(self, db: Session, owner_id: str, name: str, description: str, disciplines: list):
        db_project = Project(
            owner_id=uuid.UUID(owner_id),
            name=name,
            description=description,
            disciplines=disciplines
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    def list_user_projects(self, db: Session, user_id: str, skip: int, limit: int):
        return db.query(Project).filter(Project.owner_id == uuid.UUID(user_id)).offset(skip).limit(limit).all()

    def update_project(self, db: Session, project: Project, project_data: ProjectUpdate):
        update_data = project_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        db.commit()
        db.refresh(project)
        return project

    def delete_project(self, db: Session, project: Project):
        db.delete(project)
        db.commit()

    def add_member(self, db: Session, project_id: str, member_email: str, role: str):
        user = db.query(User).filter(User.email == member_email).first()
        if not user:
            return None
        db_member = ProjectMember(
            project_id=uuid.UUID(project_id),
            user_id=user.id,
            role=role
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member

    def list_members(self, db: Session, project_id: str):
        return db.query(ProjectMember).filter(ProjectMember.project_id == uuid.UUID(project_id)).all()

    def remove_member(self, db: Session, project_id: str, user_id: str):
        db.query(ProjectMember).filter(
            ProjectMember.project_id == uuid.UUID(project_id),
            ProjectMember.user_id == uuid.UUID(user_id)
        ).delete()
        db.commit()
