"""FastAPI application entrypoint for one8 FitLab."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import catalog, recommend, scan, scans, size
from .services import cv_pipeline

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI Fit & Performance Studio API for the one8 brand.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router)
app.include_router(scan.router)
app.include_router(size.router)
app.include_router(recommend.router)
app.include_router(scans.router)


@app.get("/", tags=["meta"])
def root():
    return {"name": settings.app_name, "status": "ok"}


@app.get("/health", tags=["meta"])
def health():
    """Health check + capability report (useful for demo/warmup)."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "cv_available": cv_pipeline.cv_available(),
        "supabase_configured": bool(settings.supabase_url),
        "hosted_inference_configured": bool(
            settings.hf_api_token or settings.nvidia_api_key
        ),
    }
