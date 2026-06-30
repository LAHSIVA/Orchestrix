from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.users import router as user_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# Register routers
app.include_router(user_router)


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