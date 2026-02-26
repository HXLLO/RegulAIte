from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Base router with common prefix and tags
base_router = APIRouter(
    prefix="/api",
    tags=["regul_aite"],
    responses={404: {"description": "Not found"}},
)

@base_router.get("/health")
async def health_check():
    """Health check endpoint for the RegulAite API."""
    return {"status": "healthy", "service": "RegulAite API"}

# Export the router for other modules to use
__all__ = ["base_router"]
