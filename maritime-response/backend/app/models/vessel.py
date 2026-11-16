from sqlalchemy import Boolean, Column, Float, Integer, String

from app.database.database import Base


class Vessel(Base):
    __tablename__ = "vessels"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    registration_number = Column(
        String(100),
        unique=True,
        nullable=False
    )

    captain = Column(
        String(100),
        nullable=False
    )

    latitude = Column(
        Float,
        nullable=False
    )

    longitude = Column(
        Float,
        nullable=False
    )

    speed = Column(
        Float,
        default=0
    )

    # AIS course / heading in degrees
    course = Column(
        Float,
        nullable=True
    )

    destination = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(30),
        default="ACTIVE"
    )

    is_active = Column(
        Boolean,
        default=True
    )