from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from app.config import settings
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    
    user_id = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    
    if user is None:
        raise credentials_exception
    
    return user

def verify_project_access(db: Session, project_id: str, user_id: str, require_owner: bool = False):
    """Verify user has access to project"""
    from app.models.project import Project, ProjectMember
    
    project = db.query(Project).filter(Project.id == uuid.UUID(project_id)).first()
    
    if not project:
        return None
    
    if require_owner and str(project.owner_id) != user_id:
        return None
    
    # Check if user is member or owner
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == uuid.UUID(project_id),
        ProjectMember.user_id == uuid.UUID(user_id)
    ).first()
    
    if is_member or str(project.owner_id) == user_id:
        return project
    
    return None