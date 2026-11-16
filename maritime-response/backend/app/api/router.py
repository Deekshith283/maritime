from fastapi import APIRouter

from app.api.v1.auth.routes import router as auth_router
from app.api.v1.vessels.routes import router as vessels_router
from app.api.v1.incidents.routes import router as incidents_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(vessels_router)
api_router.include_router(incidents_router)


@api_router.get("/health")
def health():
    return {
        "status": "healthy"
    }