from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.vessel import Vessel


router = APIRouter(
    prefix="/vessels",
    tags=["Vessels"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_vessels(
    db: Session = Depends(get_db),
):
    vessels = db.query(Vessel).all()

    return [
        {
            "id": vessel.id,
            "name": vessel.name,
            "registration_number": vessel.registration_number,
            "captain": vessel.captain,
            "latitude": vessel.latitude,
            "longitude": vessel.longitude,
            "speed": vessel.speed,

            # AIS course / heading
            "course": vessel.course,

            "destination": vessel.destination,
            "status": vessel.status,
            "is_active": vessel.is_active,
        }
        for vessel in vessels
    ]