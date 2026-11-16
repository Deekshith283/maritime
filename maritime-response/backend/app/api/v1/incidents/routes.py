from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.incident import Incident

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).all()

    return [
        {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "severity": incident.severity,
            "status": incident.status,
            "reported_by": incident.reported_by,
        }
        for incident in incidents
    ]