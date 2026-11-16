from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.mqtt.subscriber import start_mqtt
from app.api.router import api_router
from app.config.settings import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Maritime Safety and Rescue Coordination Platform",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.6:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(api_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Maritime Safety Platform API",
        "version": settings.APP_VERSION,
        "status": "running",
    }


# ============================================================
# START MQTT
# ============================================================

@app.on_event("startup")
def startup_event():
    start_mqtt()