from sqlalchemy import Column, Float, Integer, String, Text

from app.database.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)

    description = Column(Text)

    latitude = Column(Float, nullable=False)

    longitude = Column(Float, nullable=False)

    severity = Column(String(20), default="LOW")

    status = Column(String(30), default="ACTIVE")

    reported_by = Column(String(100))