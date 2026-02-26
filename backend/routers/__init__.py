"""
RegulAite API routers package.
"""

from routers.task_router import router as task_router
from routers.document_router import router as document_router
from routers.welcome_router import router as welcome_router
from routers.agents_router import router as agents_router
from routers.chat_router import router as chat_router
from routers.config_router import router as config_router
from routers.auth_router import router as auth_router
from routers.hype_router import router as hype_router

__all__ = [
    "task_router",
    "document_router",
    "welcome_router",
    "agents_router",
    "chat_router",  
    "config_router",
    "auth_router",
    "hype_router"
]