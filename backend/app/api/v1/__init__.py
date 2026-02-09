"""API v1 router and endpoints package."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import router as endpoints_router

router = APIRouter(prefix="/api/v1", tags=["v1"])
router.include_router(endpoints_router)

__all__ = ["router"]
