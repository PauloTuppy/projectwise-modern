from fastapi import APIRouter

from . import auth, users, projects, documents, comments, workflows, notifications, dashboards

router = APIRouter()
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(projects.router)
router.include_router(documents.router)
router.include_router(comments.router)
router.include_router(workflows.router)
router.include_router(notifications.router)
router.include_router(dashboards.router)