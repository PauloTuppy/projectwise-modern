from fastapi import FastAPI, WebSocketException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from app.api.v1 import auth, users, projects, documents, comments, workflows, notifications, dashboards
from app.config import settings
from app.database import engine
from app.models import Base
from app.websocket_manager import manager

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ProjectWise Modern",
    description="Modern collaboration platform for engineering projects",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(comments.router, prefix="/api/v1", tags=["comments"])
app.include_router(workflows.router, prefix="/api/v1", tags=["workflows"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(dashboards.router, prefix="/api/v1", tags=["dashboards"])

# WebSocket endpoints
 @app.websocket("/ws/documents/{document_id}")
async def websocket_document_endpoint(websocket, document_id: str):
    await manager.connect(websocket, document_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(document_id, data)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(document_id, websocket)

 @app.get("/")
async def root():
    return {"message": "ProjectWise Modern API", "version": "1.0.0"}

 @app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)