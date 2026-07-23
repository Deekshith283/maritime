"""
Maritime Safety Backend API
FastAPI-based cloud backend for alert correlation and dashboard operations
"""
from fastapi import FastAPI, Depends, HTTPException, WebSocket, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import json
import asyncio
import redis
from redis_streams import RedisStreams
import jwt
from passlib.context import CryptContext
import logging
from geopy.distance import geodesic
import uuid
import aiohttp

# ========== Configuration ==========
app = FastAPI(title="Maritime Safety Platform API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DATABASE_URL = "postgresql://user:password@localhost/maritime_safety"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis for messaging
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
streams = RedisStreams(redis_client)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"

# ========== Database Models ==========
class UserRole(str, Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    RESPONDER = "responder"
    VIEWER = "viewer"
    CREW = "crew"

class AlertState(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    URGENCY = "urgency"
    DISTRESS = "distress"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class CommunicationChannel(str, Enum):
    VHF_DSC = "vhf_dsc"
    SATELLITE = "satellite"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default=UserRole.VIEWER)
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=True)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    vessel = relationship("Vessel", back_populates="crew")
    acknowledgments = relationship("AlertAcknowledgment", back_populates="user")

class Vessel(Base):
    __tablename__ = "vessels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    mmsi = Column(String, unique=True)  # Maritime Mobile Service Identity
    imo = Column(String, unique=True)   # International Maritime Organization number
    call_sign = Column(String)
    vessel_type = Column(String)
    length = Column(Float)
    width = Column(Float)
    draft = Column(Float)
    owner = Column(String)
    home_port = Column(String)
    current_lat = Column(Float)
    current_lon = Column(Float)
    current_speed = Column(Float)
    current_heading = Column(Float)
    last_seen = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    crew = relationship("User", back_populates="vessel")
    alerts = relationship("Alert", back_populates="vessel")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now(), index=True)
    state = Column(String, default=AlertState.NORMAL.value)
    risk_score = Column(Float)
    confidence = Column(Float)
    sensor_data = Column(JSON)  # Raw sensor readings
    triggered_rules = Column(JSON)  # List of triggered rule names
    location = Column(JSON)  # {lat: float, lon: float}
    description = Column(Text)
    requires_acknowledgment = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    sla_start = Column(DateTime)
    sla_end = Column(DateTime, nullable=True)
    sla_breached = Column(Boolean, default=False)
    
    vessel = relationship("Vessel", back_populates="alerts")
    acknowledgments = relationship("AlertAcknowledgment", back_populates="alert")
    dispatches = relationship("AlertDispatch", back_populates="alert")
    timeline = relationship("IncidentTimeline", back_populates="alert")

class AlertAcknowledgment(Base):
    __tablename__ = "alert_acknowledgments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    acknowledged_at = Column(DateTime, default=func.now())
    notes = Column(Text)
    
    alert = relationship("Alert", back_populates="acknowledgments")
    user = relationship("User", back_populates="acknowledgments")

class AlertDispatch(Base):
    __tablename__ = "alert_dispatches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    channel = Column(String)
    dispatched_at = Column(DateTime, default=func.now())
    status = Column(String)  # sent, delivered, failed
    response = Column(JSON, nullable=True)
    
    alert = relationship("Alert", back_populates="dispatches")

class IncidentTimeline(Base):
    __tablename__ = "incident_timeline"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    event_type = Column(String)  # state_change, acknowledgment, dispatch, note
    data = Column(JSON)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    alert = relationship("Alert", back_populates="timeline")

class RescueStation(Base):
    __tablename__ = "rescue_stations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String)  # coast_guard, port_authority, hospital, etc.
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    contact_number = Column(String)
    email = Column(String)
    capabilities = Column(JSON)  # List of capabilities
    radius_km = Column(Float)  # Coverage radius
    is_active = Column(Boolean, default=True)

class ResponseTask(Base):
    __tablename__ = "response_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String)  # pending, in_progress, completed, cancelled
    priority = Column(Integer)  # 1-5, 1 highest
    created_at = Column(DateTime, default=func.now())
    due_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)

class HealthCheck(Base):
    __tablename__ = "health_checks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    vessel_id = Column(String, ForeignKey("vessels.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    check_type = Column(String)  # system, sensor, communication
    status = Column(String)  # healthy, warning, critical
    data = Column(JSON)
    message = Column(Text)

# ========== Pydantic Schemas ==========
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    vessel_id: Optional[str] = None
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    vessel_id: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class AlertCreate(BaseModel):
    vessel_id: str
    risk_score: float
    confidence: float
    sensor_data: Dict[str, Any]
    triggered_rules: List[str]
    location: Dict[str, float]
    description: str

class AlertResponse(BaseModel):
    id: str
    vessel_id: str
    timestamp: datetime
    state: AlertState
    risk_score: float
    confidence: float
    location: Dict[str, float]
    description: str
    requires_acknowledgment: bool
    sla_breached: bool
    
    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    state: Optional[AlertState] = None
    description: Optional[str] = None

class AcknowledgmentCreate(BaseModel):
    alert_id: str
    notes: Optional[str] = None

class DispatchRequest(BaseModel):
    alert_id: str
    channels: List[CommunicationChannel]
    message: Optional[str] = None

class GeofenceRequest(BaseModel):
    lat: float
    lon: float
    radius_km: float = 100

class SituationSummary(BaseModel):
    alert_id: str
    summary: str
    key_events: List[Dict[str, Any]]
    recommendations: List[str]

# ========== Dependency Injection ==========
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user

def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker

# ========== Core Services ==========
class AlertCorrelationService:
    """Correlates alerts from multiple sources"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def correlate_alerts(self, new_alert: Alert) -> List[Alert]:
        """Find related alerts for correlation"""
        # Find alerts from same vessel in last hour
        recent_alerts = self.db.query(Alert).filter(
            Alert.vessel_id == new_alert.vessel_id,
            Alert.timestamp >= datetime.now() - timedelta(hours=1),
            Alert.id != new_alert.id
        ).all()
        
        # Find alerts in nearby location
        nearby_alerts = []
        if new_alert.location:
            lat = new_alert.location.get('lat')
            lon = new_alert.location.get('lon')
            if lat and lon:
                # Simplified - in production use PostGIS
                nearby_alerts = self.db.query(Alert).filter(
                    Alert.timestamp >= datetime.now() - timedelta(hours=2)
                ).all()
                nearby_alerts = [
                    a for a in nearby_alerts 
                    if a.location and 
                    geodesic((lat, lon), (a.location.get('lat'), a.location.get('lon'))).km < 50
                ]
        
        return list(set(recent_alerts + nearby_alerts))

class MultiChannelDispatcher:
    """Dispatches alerts through multiple channels"""
    
    def __init__(self):
        self.channel_handlers = {
            CommunicationChannel.SMS: self._send_sms,
            CommunicationChannel.EMAIL: self._send_email,
            CommunicationChannel.PUSH: self._send_push,
            CommunicationChannel.WEBHOOK: self._send_webhook,
            CommunicationChannel.VHF_DSC: self._send_vhf_dsc,
            CommunicationChannel.SATELLITE: self._send_satellite,
        }
    
    async def dispatch(self, alert: Alert, channels: List[CommunicationChannel], 
                      custom_message: Optional[str] = None) -> List[Dict[str, Any]]:
        """Dispatch alert through specified channels"""
        results = []
        
        for channel in channels:
            handler = self.channel_handlers.get(channel)
            if handler:
                try:
                    result = await handler(alert, custom_message)
                    results.append({
                        "channel": channel,
                        "status": "sent",
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "channel": channel,
                        "status": "failed",
                        "error": str(e)
                    })
        
        return results
    
    async def _send_sms(self, alert: Alert, message: Optional[str] = None):
        """Send SMS alert"""
        # Integrate with SMS gateway (Twilio, etc.)
        async with aiohttp.ClientSession() as session:
            # Example with Twilio
            pass
    
    async def _send_email(self, alert: Alert, message: Optional[str] = None):
        """Send email alert"""
        # Integrate with email service
        pass
    
    async def _send_push(self, alert: Alert, message: Optional[str] = None):
        """Send push notification"""
        # Integrate with Firebase/APNS
        pass
    
    async def _send_webhook(self, alert: Alert, message: Optional[str] = None):
        """Send webhook to external systems"""
        # Send to configured webhooks
        pass
    
    async def _send_vhf_dsc(self, alert: Alert, message: Optional[str] = None):
        """Send VHF/DSC alert"""
        # Integrate with VHF/DSC gateway
        pass
    
    async def _send_satellite(self, alert: Alert, message: Optional[str] = None):
        """Send satellite alert"""
        # Integrate with satellite modem
        pass

class SARRoutingService:
    """Search and Rescue routing service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_nearest_resources(self, lat: float, lon: float, radius_km: float = 100) -> Dict[str, Any]:
        """Find nearest rescue stations and vessels"""
        # Get all rescue stations
        stations = self.db.query(RescueStation).filter(RescueStation.is_active == True).all()
        
        # Calculate distances
        nearest_stations = []
        for station in stations:
            distance = geodesic((lat, lon), (station.lat, station.lon)).km
            if distance <= radius_km:
                station_dict = {
                    "id": station.id,
                    "name": station.name,
                    "type": station.type,
                    "distance_km": round(distance, 2),
                    "contact": station.contact_number,
                    "capabilities": station.capabilities
                }
                nearest_stations.append(station_dict)
        
        # Get nearby vessels (from AIS data)
        nearby_vessels = self.db.query(Vessel).filter(
            Vessel.is_active == True,
            Vessel.id != "current_vessel_id"  # Exclude current vessel
        ).all()
        
        nearest_vessels = []
        for vessel in nearby_vessels:
            if vessel.current_lat and vessel.current_lon:
                distance = geodesic((lat, lon), (vessel.current_lat, vessel.current_lon)).km
                if distance <= radius_km:
                    vessel_dict = {
                        "id": vessel.id,
                        "name": vessel.name,
                        "mmsi": vessel.mmsi,
                        "distance_km": round(distance, 2),
                        "speed": vessel.current_speed,
                        "heading": vessel.current_heading
                    }
                    nearest_vessels.append(vessel_dict)
        
        # Sort by distance
        nearest_stations.sort(key=lambda x: x["distance_km"])
        nearest_vessels.sort(key=lambda x: x["distance_km"])
        
        return {
            "stations": nearest_stations[:5],  # Top 5 nearest
            "vessels": nearest_vessels[:10],   # Top 10 nearest
            "search_center": {"lat": lat, "lon": lon},
            "search_radius": radius_km
        }       
    