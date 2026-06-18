from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
title=settings.APP_NAME,
version=settings.APP_VERSION
)

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
