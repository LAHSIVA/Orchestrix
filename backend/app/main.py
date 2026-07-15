from fastapi import FastAPI

import app.db.base

from app.core.config import settings
from app.api.v1.users import router as user_router
from app.api.v1.workflow_definitions import router as workflow_definition_router
from app.api.v1.workflow_steps import router as workflow_step_router
from app.api.v1.workflow_instances import router as workflow_instance_router
from app.api.v1.approval_tasks import (
    router as approval_task_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# Register routers
app.include_router(user_router)
app.include_router(workflow_definition_router)
app.include_router(workflow_step_router)
app.include_router(workflow_instance_router)
app.include_router(approval_task_router)

@app.get("/")
async def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }