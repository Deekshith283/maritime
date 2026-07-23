"""
Maritime Safety Edge Agent
Operates offline-first with local storage and sync capability
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import pickle
from pathlib import Path

# ========== Data Models ==========
class AlertState(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    URGENCY = "urgency"
    DISTRESS = "distress"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

@dataclass
class SensorReading:
    timestamp: datetime
    gps_lat: float
    gps_lon: float
    gps_accuracy: float
    imu_roll: float
    imu_pitch: float
    imu_yaw: float
    water_level: float  # mm
    fire_detected: bool
    engine_temp: float  # °C
    engine_rpm: int
    battery_voltage: float
    ais_data: Dict[str, Any] = None
    
@dataclass
class AlertEvent:
    id: str
    timestamp: datetime
    state: AlertState
    risk_score: float
    confidence: float
    sensor_data: SensorReading
    triggered_rules: List[str]
    location: Dict[str, float]
    description: str
    requires_acknowledgment: bool = False
    acknowledged_by: str = None
    acknowledged_at: datetime = None

# ========== Event Fusion Engine ==========
class EventFusionEngine:
    """Combines multiple sensor inputs into unified risk score"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = self._load_safety_rules()
        
    def _load_safety_rules(self) -> List[Dict]:
        """Load deterministic safety rules"""
        return [
            {
                "name": "water_ingress_critical",
                "condition": lambda s: s.water_level > 500,  # 500mm threshold
                "risk_score": 90,
                "state": AlertState.DISTRESS
            },
            {
                "name": "fire_detected",
                "condition": lambda s: s.fire_detected,
                "risk_score": 95,
                "state": AlertState.DISTRESS
            },
            {
                "name": "engine_overheat",
                "condition": lambda s: s.engine_temp > 120,
                "risk_score": 75,
                "state": AlertState.URGENCY
            },
            {
                "name": "severe_tilt",
                "condition": lambda s: abs(s.imu_roll) > 30 or abs(s.imu_pitch) > 30,
                "risk_score": 85,
                "state": AlertState.DISTRESS
            }
        ]
    
    def calculate_risk_score(self, sensor_data: SensorReading) -> Dict[str, Any]:
        """Calculate comprehensive risk score from all sensors"""
        scores = []
        triggered_rules = []
        
        # Apply deterministic rules
        for rule in self.rules:
            if rule["condition"](sensor_data):
                scores.append(rule["risk_score"])
                triggered_rules.append(rule["name"])
        
        # Apply ML anomaly detection (simplified)
        ml_score = self._ml_anomaly_detection(sensor_data)
        if ml_score > 50:
            scores.append(ml_score)
            triggered_rules.append("ml_anomaly")
        
        # Calculate final score
        final_score = max(scores) if scores else 0
        
        # Determine alert state
        state = self._determine_alert_state(final_score, triggered_rules)
        
        return {
            "risk_score": final_score,
            "confidence": self._calculate_confidence(sensor_data),
            "triggered_rules": triggered_rules,
            "recommended_state": state
        }
    
    def _ml_anomaly_detection(self, sensor_data: SensorReading) -> float:
        """ML-based anomaly detection (simplified for edge)"""
        # In production, use trained model
        anomalies = []
        
        # Check for unusual patterns
        if sensor_data.gps_accuracy > 50:  # Poor GPS
            anomalies.append(40)
        if abs(sensor_data.imu_roll) > 15:  # Moderate tilt
            anomalies.append(60)
        if sensor_data.battery_voltage < 11.5:  # Low battery
            anomalies.append(30)
            
        return max(anomalies) if anomalies else 0
    
    def _calculate_confidence(self, sensor_data: SensorReading) -> float:
        """Calculate confidence in sensor readings"""
        confidence_factors = []
        
        # GPS confidence
        if sensor_data.gps_accuracy < 10:
            confidence_factors.append(0.9)
        elif sensor_data.gps_accuracy < 25:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Sensor health checks
        if sensor_data.battery_voltage > 12:
            confidence_factors.append(0.8)
        
        # Return average confidence
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _determine_alert_state(self, risk_score: float, rules: List[str]) -> AlertState:
        """Map risk score to alert state"""
        if risk_score >= 90:
            return AlertState.DISTRESS
        elif risk_score >= 70:
            return AlertState.URGENCY
        elif risk_score >= 40:
            return AlertState.WARNING
        else:
            return AlertState.NORMAL

# ========== Alert State Machine ==========
class AlertStateMachine:
    """Manages alert lifecycle with configurable timeouts"""
    
    def __init__(self):
        self.state_transitions = {
            AlertState.NORMAL: [AlertState.WARNING, AlertState.URGENCY, AlertState.DISTRESS],
            AlertState.WARNING: [AlertState.NORMAL, AlertState.URGENCY, AlertState.DISTRESS],
            AlertState.URGENCY: [AlertState.WARNING, AlertState.DISTRESS, AlertState.ACKNOWLEDGED],
            AlertState.DISTRESS: [AlertState.ACKNOWLEDGED, AlertState.RESOLVED],
            AlertState.ACKNOWLEDGED: [AlertState.RESOLVED, AlertState.DISTRESS],
            AlertState.RESOLVED: [AlertState.NORMAL]
        }
        
        self.escalation_timeouts = {
            AlertState.WARNING: 300,  # 5 minutes
            AlertState.URGENCY: 120,  # 2 minutes
            AlertState.DISTRESS: 60   # 1 minute
        }
        
        self.active_alerts: Dict[str, AlertEvent] = {}
    
    def transition(self, alert_id: str, new_state: AlertState, 
                   reason: str = None) -> bool:
        """Transition alert to new state if valid"""
        if alert_id not in self.active_alerts:
            return False
            
        current_state = self.active_alerts[alert_id].state
        
        if new_state in self.state_transitions.get(current_state, []):
            self.active_alerts[alert_id].state = new_state
            self.active_alerts[alert_id].description = f"{reason} - State changed from {current_state.value} to {new_state.value}"
            
            # Log transition
            self._log_transition(alert_id, current_state, new_state)
            return True
            
        return False
    
    def check_escalation(self, alert_id: str) -> bool:
        """Check if alert needs escalation based on timeout"""
        alert = self.active_alerts.get(alert_id)
        if not alert:
            return False
            
        time_in_state = (datetime.now() - alert.timestamp).total_seconds()
        timeout = self.escalation_timeouts.get(alert.state)
        
        if timeout and time_in_state > timeout:
            # Auto-escalate
            if alert.state == AlertState.WARNING:
                return self.transition(alert_id, AlertState.URGENCY, "Auto-escalation: timeout")
            elif alert.state == AlertState.URGENCY:
                return self.transition(alert_id, AlertState.DISTRESS, "Auto-escalation: timeout")
                
        return False

# ========== Offline Storage ==========
class LocalStorage:
    """SQLite-based offline storage for alerts and sensor data"""
    
    def __init__(self, db_path: str = "maritime_data.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                state TEXT,
                risk_score REAL,
                confidence REAL,
                sensor_data BLOB,
                triggered_rules TEXT,
                location TEXT,
                description TEXT,
                requires_acknowledgment BOOLEAN,
                acknowledged_by TEXT,
                acknowledged_at DATETIME,
                synced BOOLEAN DEFAULT 0
            )
        ''')
        
        # Sensor readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                data BLOB
            )
        ''')
        
        # Sync queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT,
                record_id TEXT,
                operation TEXT,
                data BLOB,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_alert(self, alert: AlertEvent):
        """Save alert to local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO alerts 
            (id, timestamp, state, risk_score, confidence, sensor_data, 
             triggered_rules, location, description, requires_acknowledgment,
             acknowledged_by, acknowledged_at, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.id,
            alert.timestamp.isoformat(),
            alert.state.value,
            alert.risk_score,
            alert.confidence,
            pickle.dumps(alert.sensor_data),
            json.dumps(alert.triggered_rules),
            json.dumps(alert.location),
            alert.description,
            alert.requires_acknowledgment,
            alert.acknowledged_by,
            alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            0  # Not synced
        ))
        
        # Add to sync queue
        cursor.execute('''
            INSERT INTO sync_queue (table_name, record_id, operation, data)
            VALUES (?, ?, ?, ?)
        ''', (
            'alerts',
            alert.id,
            'UPSERT',
            pickle.dumps(alert)
        ))
        
        conn.commit()
        conn.close()

# ========== Main Edge Agent ==========
class MaritimeEdgeAgent:
    """Main edge agent coordinating all components"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.fusion_engine = EventFusionEngine(self.config)
        self.state_machine = AlertStateMachine()
        self.storage = LocalStorage()
        self.alert_dispatcher = AlertDispatcher(self.config)
        
        # Health monitoring
        self.health_monitor = HealthMonitor()
        
        # Event correlation for false-alarm suppression
        self.event_correlator = EventCorrelator()
        
        # Tamper detection
        self.tamper_detector = TamperDetector()
        
        # Sync manager for offline-first operation
        self.sync_manager = SyncManager(self.config.get("cloud_endpoint"))
        
        self.running = False
        
    async def run(self):
        """Main event loop"""
        self.running = True
        logging.info("Maritime Edge Agent started")
        
        while self.running:
            try:
                # 1. Collect sensor data
                sensor_data = await self._collect_sensor_data()
                
                # 2. Check for tampering
                tamper_status = self.tamper_detector.check(sensor_data)
                if tamper_status["tampered"]:
                    self._handle_tampering(tamper_status)
                
                # 3. Calculate risk score
                risk_assessment = self.fusion_engine.calculate_risk_score(sensor_data)
                
                # 4. Check event correlation for false-alarm suppression
                should_alert = self.event_correlator.correlate(
                    sensor_data, 
                    risk_assessment
                )
                
                if should_alert and risk_assessment["risk_score"] > 0:
                    # 5. Create alert
                    alert = self._create_alert(sensor_data, risk_assessment)
                    
                    # 6. Save locally
                    self.storage.save_alert(alert)
                    
                    # 7. Add to state machine
                    self.state_machine.active_alerts[alert.id] = alert
                    
                    # 8. Dispatch alert if connectivity available
                    if self._check_connectivity():
                        await self.alert_dispatcher.dispatch(alert)
                    else:
                        logging.warning("No connectivity, alert stored locally")
                
                # 9. Check for escalations
                for alert_id in list(self.state_machine.active_alerts.keys()):
                    self.state_machine.check_escalation(alert_id)
                
                # 10. Run health checks
                health_status = self.health_monitor.check()
                if not health_status["healthy"]:
                    logging.error(f"Health check failed: {health_status}")
                
                # 11. Attempt sync if pending
                if self._check_connectivity():
                    await self.sync_manager.sync_pending_data(self.storage)
                
                # 12. Sleep before next cycle
                await asyncio.sleep(self.config.get("polling_interval", 5))
                
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                await asyncio.sleep(10)  # Back off on error

# ========== Additional Components ==========
class AlertDispatcher:
    """Multi-channel alert dispatcher"""
    
    async def dispatch(self, alert: AlertEvent):
        """Dispatch alert through available channels"""
        channels = self.config.get("alert_channels", [])
        
        for channel in channels:
            try:
                if channel["type"] == "satellite":
                    await self._send_via_satellite(alert, channel)
                elif channel["type"] == "vhf_dsc":
                    await self._send_via_vhf_dsc(alert, channel)
                elif channel["type"] == "sms":
                    await self._send_via_sms(alert, channel)
                # Add more channels as needed
            except Exception as e:
                logging.error(f"Failed to dispatch via {channel['type']}: {e}")

class HealthMonitor:
    """Continuous health monitoring"""
    
    def check(self) -> Dict[str, Any]:
        return {
            "healthy": True,
            "gps_lock": self._check_gps_lock(),
            "battery_level": self._check_battery(),
            "sensors_ok": self._check_sensors(),
            "storage_available": self._check_storage(),
            "connectivity": self._check_connectivity()
        }

class EventCorrelator:
    """False-alarm suppression through event correlation"""
    
    def correlate(self, sensor_data: SensorReading, risk_assessment: Dict) -> bool:
        """Return True if events are correlated enough to trigger alert"""
        # Implement correlation logic
        # Check multiple sensor confirmations
        # Check temporal patterns
        # Check location consistency
        return True  # Simplified

class TamperDetector:
    """Detect device tampering"""
    
    def check(self, sensor_data: SensorReading) -> Dict[str, Any]:
        tamper_indicators = []
        
        # Check for sudden GPS changes (spoofing)
        if self._check_gps_spoofing(sensor_data):
            tamper_indicators.append("gps_spoofing")
        
        # Check for sensor disconnection
        if self._check_sensor_disconnect(sensor_data):
            tamper_indicators.append("sensor_disconnect")
        
        # Check for power anomalies
        if self._check_power_tamper(sensor_data):
            tamper_indicators.append("power_tamper")
        
        return {
            "tampered": len(tamper_indicators) > 0,
            "indicators": tamper_indicators
        }

class SyncManager:
    """Manage offline sync with cloud"""
    
    async def sync_pending_data(self, storage: LocalStorage):
        """Sync pending data to cloud"""
        # Implement sync logic
        pass

# ========== Main Entry Point ==========
async def main():
    """Main entry point for edge agent"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    agent = MaritimeEdgeAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())