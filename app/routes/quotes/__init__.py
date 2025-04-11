
from fastapi import APIRouter
from backend.app.routes.quotes.list import router as list_router
from backend.app.routes.quotes.details import router as details_router
from backend.app.routes.quotes.create import router as create_router
from backend.app.routes.quotes.manage import router as manage_router

# Main quotes router
router = APIRouter(tags=["quotes"], prefix="/quotes")

# Include sub-routers
router.include_router(list_router)
router.include_router(details_router)
router.include_router(create_router)
router.include_router(manage_router)
