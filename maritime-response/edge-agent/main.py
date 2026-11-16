"""Offline-capable Edge Agent for the AI-Powered Maritime Emergency System.

AI method: an adaptive, unsupervised robust-baseline detector (median/profile
initialization + online mean/variance updates on non-anomalous samples) is
combined with deterministic maritime safety rules. This is intentionally
transparent and lightweight; it is not a pretrained neural network.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import os
import sqlite3
import time
import urllib.error
import urllib.request
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("maritime.edge")

DEFAULT_BASELINES: dict[str, dict[str, float]] = {
    "water_level_mm": {"mean": 30.0, "std": 40.0},
    "roll_deg": {"mean": 0.0, "std": 6.0},
    "pitch_deg": {"mean": 0.0, "std": 6.0},
    "engine_temp_c": {"mean": 80.0, "std": 12.0},
    "engine_rpm": {"mean": 1500.0, "std": 400.0},
    "battery_voltage": {"mean": 12.6, "std": 0.45},
    "gps_accuracy_m": {"mean": 5.0, "std": 5.0},
}

REQUIRED_SENSOR_FIELDS = [
    "gps_accuracy_m", "roll_deg", "pitch_deg", "yaw_deg", "water_level_mm",
    "fire_detected", "engine_temp_c", "engine_rpm", "battery_voltage", "panic_button",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


class SensorSimulator:
    """Deterministic sensor simulator for development and viva demonstrations."""

    SCENARIOS = ("normal", "fire", "flooding", "engine", "tilt", "panic", "low_battery", "auto")

    def __init__(self, vessel_id: str, scenario: str = "normal"):
        if scenario not in self.SCENARIOS:
            raise ValueError(f"Unsupported scenario '{scenario}'. Choose from {', '.join(self.SCENARIOS)}")
        self.vessel_id = vessel_id
        self.scenario = scenario
        self.counter = 0
        self.latitude = 12.90
        self.longitude = 74.84

    def read(self) -> dict[str, Any]:
        self.counter += 1
        scenario = self.scenario
        if scenario == "auto":
            # Repeated normal and abnormal windows let users observe alert creation and resolution.
            pattern = ["normal", "normal", "fire", "fire", "normal", "flooding", "flooding", "normal", "engine", "normal", "panic", "normal"]
            scenario = pattern[(self.counter - 1) % len(pattern)]

        self.latitude += 0.00015
        self.longitude += 0.00010
        reading: dict[str, Any] = {
            "gps_accuracy_m": 4.5,
            "roll_deg": 2.0,
            "pitch_deg": 1.0,
            "yaw_deg": 92.0,
            "water_level_mm": 28.0,
            "fire_detected": False,
            "engine_temp_c": 82.0,
            "engine_rpm": 1480,
            "battery_voltage": 12.6,
            "panic_button": False,
            "speed_knots": 8.4,
            "heading_deg": 92.0,
            "ais_data": {
                "mmsi": "419000001",
                "course_over_ground": 92.0,
                "navigation_status": "under_way",
            },
        }
        if scenario == "fire":
            reading.update(fire_detected=True, engine_temp_c=128.0)
        elif scenario == "flooding":
            reading.update(water_level_mm=650.0)
        elif scenario == "engine":
            reading.update(engine_temp_c=132.0, engine_rpm=500)
        elif scenario == "tilt":
            reading.update(roll_deg=38.0, pitch_deg=12.0)
        elif scenario == "panic":
            reading.update(panic_button=True)
        elif scenario == "low_battery":
            reading.update(battery_voltage=10.5)
        return reading


class AdaptiveAnomalyDetector:
    """Lightweight adaptive robust z-score detector suitable for edge devices.

    Baselines start from documented normal operating profiles. The model only
    updates from samples within a stable band, which reduces contamination by
    obvious abnormal readings. Scores are anomaly indicators, not probabilities.
    """

    MODEL_NAME = "adaptive_robust_baseline"
    MODEL_VERSION = "1.0"

    def __init__(self, state_path: Path, contamination_guard_z: float = 2.8):
        self.state_path = state_path
        self.contamination_guard_z = contamination_guard_z
        self.stats: dict[str, dict[str, float]] = {
            key: {"mean": val["mean"], "m2": (val["std"] ** 2) * 19, "count": 20}
            for key, val in DEFAULT_BASELINES.items()
        }
        self._load_state()

    def _load_state(self) -> None:
        if not self.state_path.exists():
            return
        try:
            saved = json.loads(self.state_path.read_text(encoding="utf-8"))
            for key, item in saved.items():
                if key in self.stats and all(k in item for k in ("mean", "m2", "count")):
                    self.stats[key] = {"mean": float(item["mean"]), "m2": float(item["m2"]), "count": int(item["count"])}
        except (OSError, ValueError, TypeError):
            LOGGER.warning("Could not read baseline state; starting from default operating profiles")

    def _save_state(self) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(self.stats, indent=2), encoding="utf-8")
        except OSError:
            LOGGER.exception("Could not persist adaptive model baseline")

    def assess(self, sensor_data: dict[str, Any]) -> dict[str, Any]:
        feature_results: list[dict[str, Any]] = []
        for feature, stats in self.stats.items():
            if feature not in sensor_data:
                continue
            value = safe_float(sensor_data[feature], stats["mean"])
            count = max(stats["count"], 2)
            variance = stats["m2"] / max(count - 1, 1)
            std = max(math.sqrt(max(variance, 0.0)), DEFAULT_BASELINES[feature]["std"] * 0.35, 0.05)
            z_score = abs(value - stats["mean"]) / std
            score = min(100.0, (z_score / 6.0) * 100.0)
            feature_results.append({
                "feature": feature,
                "value": round(value, 3),
                "baseline_mean": round(stats["mean"], 3),
                "z_score": round(z_score, 3),
                "anomaly_score": round(score, 1),
            })
            # Learn only from readings sufficiently close to the current baseline.
            if z_score <= self.contamination_guard_z:
                new_count = count + 1
                delta = value - stats["mean"]
                new_mean = stats["mean"] + delta / new_count
                delta_after = value - new_mean
                stats["m2"] += delta * delta_after
                stats["mean"] = new_mean
                stats["count"] = new_count

        feature_results.sort(key=lambda item: item["anomaly_score"], reverse=True)
        anomaly_score = feature_results[0]["anomaly_score"] if feature_results else 0.0
        self._save_state()
        return {
            "model_name": self.MODEL_NAME,
            "model_version": self.MODEL_VERSION,
            "method": "online adaptive robust z-score against operating baselines",
            "anomaly_detected": anomaly_score >= 65.0,
            "anomaly_score": round(anomaly_score, 1),
            "anomalous_features": feature_results[:4],
            "baseline_samples": {key: int(value["count"]) for key, value in self.stats.items()},
        }


class MaritimeRiskEngine:
    """Combines non-negotiable maritime rules with adaptive anomaly scoring."""

    def __init__(self, detector: AdaptiveAnomalyDetector):
        self.detector = detector

    def analyse(self, sensor_data: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        ai = self.detector.assess(sensor_data)
        rules: list[str] = []
        events: list[dict[str, Any]] = []

        def add_event(code: str, title: str, severity: str, score: float, description: str, action: str) -> None:
            rules.append(code.lower())
            events.append({
                "code": code,
                "title": title,
                "severity": severity,
                "risk_score": float(score),
                "description": description,
                "recommended_action": action,
            })

        water = safe_float(sensor_data.get("water_level_mm"))
        engine_temp = safe_float(sensor_data.get("engine_temp_c"))
        roll = abs(safe_float(sensor_data.get("roll_deg")))
        pitch = abs(safe_float(sensor_data.get("pitch_deg")))
        battery = safe_float(sensor_data.get("battery_voltage"))

        if bool(sensor_data.get("panic_button")):
            add_event("PANIC", "Crew panic / SOS activated", "CRITICAL", 100,
                      "The onboard panic button has been activated.",
                      "Treat this as a distress call. Confirm crew safety and initiate the vessel emergency response procedure.")
        if bool(sensor_data.get("fire_detected")):
            add_event("FIRE", "Fire detected onboard", "CRITICAL", 100,
                      "The fire sensor reports an active fire condition.",
                      "Raise the fire alarm, follow the vessel fire plan and request emergency assistance.")
        if water >= 500:
            add_event("FLOODING", "Critical water ingress", "CRITICAL", 96,
                      f"Water ingress reading is {water:.0f} mm, above the 500 mm critical limit.",
                      "Check compartments and bilge pumps, isolate affected areas and transmit a distress alert if required.")
        elif water >= 300:
            add_event("WATER_INGRESS", "Elevated water ingress", "HIGH", 78,
                      f"Water ingress reading is {water:.0f} mm, above the 300 mm warning limit.",
                      "Inspect the hull and bilge system immediately and monitor the water level continuously.")
        if engine_temp >= 120:
            add_event("ENGINE_OVERHEAT", "Critical engine overheating", "CRITICAL", 92,
                      f"Engine temperature is {engine_temp:.1f} °C, above the 120 °C critical limit.",
                      "Reduce load safely, inspect cooling and lubrication systems and prepare for engine shutdown if needed.")
        elif engine_temp >= 100:
            add_event("ENGINE_OVERHEAT", "Engine temperature elevated", "HIGH", 74,
                      f"Engine temperature is {engine_temp:.1f} °C, above the 100 °C warning limit.",
                      "Inspect the cooling system and reduce engine load while monitoring temperature.")
        if roll >= 30 or pitch >= 30:
            add_event("VESSEL_TILT", "Severe vessel tilt detected", "CRITICAL", 88,
                      f"Vessel attitude is abnormal (roll {roll:.1f}°, pitch {pitch:.1f}°).",
                      "Check for capsize risk, flooding and cargo shift; alert crew and nearby response teams.")
        elif roll >= 20 or pitch >= 20:
            add_event("VESSEL_TILT", "Abnormal vessel tilt", "HIGH", 72,
                      f"Vessel attitude is outside the configured normal band (roll {roll:.1f}°, pitch {pitch:.1f}°).",
                      "Verify vessel stability and inspect for load shift, waves or water ingress.")
        if battery < 10.8:
            add_event("LOW_BATTERY", "Low edge-system battery", "MEDIUM", 48,
                      f"Battery voltage is {battery:.1f} V, below the 10.8 V warning limit.",
                      "Check the power supply and preserve backup power for emergency communications.")

        strongest_rule_score = max((event["risk_score"] for event in events), default=0.0)
        if ai["anomaly_detected"] and (not events or ai["anomaly_score"] > strongest_rule_score + 12):
            top = ai["anomalous_features"][0] if ai["anomalous_features"] else {"feature": "sensor data", "value": "unknown", "anomaly_score": ai["anomaly_score"]}
            severity = "CRITICAL" if ai["anomaly_score"] >= 90 else "HIGH"
            add_event("AI_ANOMALY", "AI detected unusual sensor behaviour", severity,
                      max(65.0, ai["anomaly_score"]),
                      f"The adaptive baseline detector found an unusual {top['feature']} reading ({top['value']}); anomaly score {ai['anomaly_score']:.1f}/100.",
                      "Verify the sensor and vessel condition. Review the AI feature deviations before escalating the response.")

        # Confidence describes sensor completeness and evidence availability; it is not a calibrated probability.
        valid_count = sum(1 for name in REQUIRED_SENSOR_FIELDS if name in sensor_data and sensor_data[name] is not None)
        completeness = valid_count / len(REQUIRED_SENSOR_FIELDS)
        corroboration = min(len(events), 2) / 2
        confidence = min(0.99, 0.55 + 0.35 * completeness + 0.09 * corroboration)
        risk_score = max([event["risk_score"] for event in events] + [ai["anomaly_score"] if ai["anomaly_detected"] else 0.0])
        if risk_score >= 90:
            risk_level = "CRITICAL"
        elif risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        ai.update({
            "confidence_score": round(confidence, 2),
            "confidence_note": "Heuristic sensor-completeness and evidence score; not a calibrated probability.",
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "triggered_rules": rules,
            "explanation": " ".join(event["description"] for event in events) if events else (
                f"No safety rule was triggered. Highest adaptive anomaly score: {ai['anomaly_score']:.1f}/100."
            ),
            "recommended_actions": [event["recommended_action"] for event in events] or [
                "Continue normal monitoring and retain sensor history for baseline updates."
            ],
        })
        return ai, events


class EdgeStore:
    """SQLite outbox: telemetry is retained until the backend confirms receipt."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS telemetry_outbox (
                event_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                delivered INTEGER NOT NULL DEFAULT 0,
                delivered_at TEXT
            )""")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_outbox_delivered ON telemetry_outbox(delivered, created_at)")

    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def enqueue(self, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO telemetry_outbox(event_id, created_at, payload_json, delivered) VALUES (?, ?, ?, 0)",
                (payload["event_id"], utc_now_iso(), json.dumps(payload, separators=(",", ":"))),
            )

    def pending(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT event_id, payload_json FROM telemetry_outbox WHERE delivered=0 ORDER BY created_at LIMIT ?", (limit,)
            ).fetchall()
        return [{"event_id": row["event_id"], "payload": json.loads(row["payload_json"])} for row in rows]

    def mark_delivered(self, event_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE telemetry_outbox SET delivered=1, delivered_at=? WHERE event_id=?",
                (utc_now_iso(), event_id),
            )

    def counts(self) -> dict[str, int]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN delivered=0 THEN 1 ELSE 0 END) AS pending FROM telemetry_outbox"
            ).fetchone()
        return {"stored": int(row["total"] or 0), "pending": int(row["pending"] or 0)}


class EdgeTransport:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def send(self, payload: dict[str, Any]) -> bool:
        mqtt_config = self.config.get("mqtt", {})
        if mqtt_config.get("enabled", False):
            # MQTT publication is an additional event-bus copy. The local outbox
            # is marked delivered only after the REST API confirms application-level
            # processing; broker PUBACK alone does not prove backend persistence.
            if not self._send_mqtt(payload, mqtt_config):
                LOGGER.warning("MQTT publish failed; REST ingestion will still be attempted")
        return self._send_http(payload)

    def _send_http(self, payload: dict[str, Any]) -> bool:
        url = self.config.get("backend_url", "http://127.0.0.1:8000/api/v1/telemetry").rstrip("/")
        if not url.endswith("/api/v1/telemetry"):
            url += "/api/v1/telemetry"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=float(self.config.get("http_timeout_seconds", 4))) as response:
                return 200 <= response.status < 300
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            LOGGER.warning("REST delivery unavailable (%s)", exc)
            return False

    def _send_mqtt(self, payload: dict[str, Any], mqtt_config: dict[str, Any]) -> bool:
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            LOGGER.warning("paho-mqtt is not installed; MQTT skipped")
            return False
        client = mqtt.Client(client_id=f"maritime-edge-{payload['vessel']['id']}")
        username = mqtt_config.get("username")
        if username:
            client.username_pw_set(username, mqtt_config.get("password"))
        try:
            client.connect(mqtt_config.get("host", "127.0.0.1"), int(mqtt_config.get("port", 1883)), keepalive=20)
            client.loop_start()
            info = client.publish(mqtt_config.get("topic", "maritime/telemetry"), json.dumps(payload), qos=1)
            info.wait_for_publish(timeout=5)
            ok = info.is_published()
            client.disconnect()
            client.loop_stop()
            return ok
        except Exception as exc:
            LOGGER.warning("MQTT delivery error: %s", exc)
            try:
                client.disconnect()
                client.loop_stop()
            except Exception:
                pass
            return False


class MaritimeEdgeAgent:
    def __init__(self, config: dict[str, Any], database_path: Path, scenario: str | None = None):
        self.config = config
        vessel_config = config.get("vessel", {})
        self.vessel_id = vessel_config.get("id", "EDGE-001")
        self.vessel_name = vessel_config.get("name", "Coastal Patrol Vessel")
        self.simulator = SensorSimulator(self.vessel_id, scenario or config.get("simulation", {}).get("scenario", "normal"))
        self.detector = AdaptiveAnomalyDetector(database_path.with_name("ai_baseline.json"))
        self.risk_engine = MaritimeRiskEngine(self.detector)
        self.store = EdgeStore(database_path)
        self.transport = EdgeTransport(config)

    def create_payload(self) -> dict[str, Any]:
        sensor_data = self.simulator.read()
        assessment, active_events = self.risk_engine.analyse(sensor_data)
        return {
            "schema_version": "1.0",
            "event_id": str(uuid.uuid4()),
            "timestamp": utc_now_iso(),
            "vessel": {
                "id": self.vessel_id,
                "name": self.vessel_name,
                "mmsi": self.config.get("vessel", {}).get("mmsi", "419000001"),
                "vessel_type": self.config.get("vessel", {}).get("type", "Coastal patrol"),
                "call_sign": self.config.get("vessel", {}).get("call_sign", "EDGE001"),
            },
            "location": {"lat": self.simulator.latitude, "lon": self.simulator.longitude},
            "sensor_data": sensor_data,
            "ai_assessment": assessment,
            "active_events": active_events,
        }

    def flush_outbox(self) -> int:
        delivered = 0
        for item in self.store.pending(limit=int(self.config.get("outbox_batch_size", 50))):
            if self.transport.send(item["payload"]):
                self.store.mark_delivered(item["event_id"])
                delivered += 1
            else:
                # Preserve ordering; retry at the next cycle rather than hammering the API.
                break
        return delivered

    def run_once(self) -> dict[str, Any]:
        payload = self.create_payload()
        self.store.enqueue(payload)
        sent = self.flush_outbox()
        result = {
            "event_id": payload["event_id"],
            "vessel_id": self.vessel_id,
            "risk_level": payload["ai_assessment"]["risk_level"],
            "risk_score": payload["ai_assessment"]["risk_score"],
            "anomaly_detected": payload["ai_assessment"]["anomaly_detected"],
            "active_events": [event["code"] for event in payload["active_events"]],
            "delivered_now": sent,
            "outbox": self.store.counts(),
        }
        LOGGER.info("Telemetry cycle: %s", json.dumps(result))
        return result

    def run(self, once: bool = False, cycles: int | None = None) -> None:
        interval = max(1.0, float(self.config.get("polling_interval_seconds", 5)))
        completed = 0
        LOGGER.info("Edge Agent started for %s (%s)", self.vessel_name, self.vessel_id)
        while True:
            self.run_once()
            completed += 1
            if once or (cycles is not None and completed >= cycles):
                break
            time.sleep(interval)


def load_config(config_path: Path) -> dict[str, Any]:
    defaults = {
        "vessel": {"id": "EDGE-001", "name": "Coastal Patrol Vessel", "mmsi": "419000001", "type": "Coastal patrol", "call_sign": "EDGE001"},
        "backend_url": "http://127.0.0.1:8000/api/v1/telemetry",
        "http_timeout_seconds": 4,
        "polling_interval_seconds": 5,
        "outbox_batch_size": 50,
        "mqtt": {"enabled": False, "host": "127.0.0.1", "port": 1883, "topic": "maritime/telemetry"},
        "simulation": {"scenario": "normal"},
        "storage": {"database_path": "data/edge_outbox.db"},
    }
    if config_path.exists():
        saved = json.loads(config_path.read_text(encoding="utf-8"))
        for key, value in saved.items():
            if isinstance(value, dict) and isinstance(defaults.get(key), dict):
                defaults[key].update(value)
            else:
                defaults[key] = value
    return defaults


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-powered maritime Edge Agent")
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--db-path", type=Path, default=None, help="Override the SQLite outbox path")
    parser.add_argument("--backend-url", type=str, default=None, help="Override backend telemetry endpoint")
    parser.add_argument("--scenario", choices=SensorSimulator.SCENARIOS, default=None, help="Sensor simulation scenario")
    parser.add_argument("--once", action="store_true", help="Run one telemetry cycle and exit")
    parser.add_argument("--cycles", type=int, default=None, help="Run a fixed number of telemetry cycles")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = parse_args()
    config = load_config(args.config)
    if args.backend_url:
        config["backend_url"] = args.backend_url
    if args.scenario:
        config.setdefault("simulation", {})["scenario"] = args.scenario
    db_path = args.db_path or Path(config.get("storage", {}).get("database_path", "data/edge_outbox.db"))
    if not db_path.is_absolute():
        db_path = (Path(__file__).parent / db_path).resolve()
    agent = MaritimeEdgeAgent(config, db_path, scenario=args.scenario)
    agent.run(once=args.once, cycles=args.cycles)


if __name__ == "__main__":
    main()
