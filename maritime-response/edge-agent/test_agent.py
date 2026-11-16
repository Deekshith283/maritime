"""Small offline unit tests: python -m unittest test_agent"""
import tempfile
import unittest
from pathlib import Path

from main import AdaptiveAnomalyDetector, EdgeStore, MaritimeRiskEngine, SensorSimulator


class EdgeAgentTests(unittest.TestCase):
    def test_fire_rule_creates_critical_event(self):
        with tempfile.TemporaryDirectory() as folder:
            detector = AdaptiveAnomalyDetector(Path(folder) / "baseline.json")
            engine = MaritimeRiskEngine(detector)
            reading = SensorSimulator("TEST-1", "fire").read()
            assessment, events = engine.analyse(reading)
            self.assertTrue(any(event["code"] == "FIRE" for event in events))
            self.assertEqual(assessment["risk_level"], "CRITICAL")

    def test_panic_rule_creates_distress_event(self):
        with tempfile.TemporaryDirectory() as folder:
            detector = AdaptiveAnomalyDetector(Path(folder) / "baseline.json")
            engine = MaritimeRiskEngine(detector)
            reading = SensorSimulator("TEST-1", "panic").read()
            _, events = engine.analyse(reading)
            self.assertTrue(any(event["code"] == "PANIC" and event["severity"] == "CRITICAL" for event in events))

    def test_normal_sample_has_no_active_events(self):
        with tempfile.TemporaryDirectory() as folder:
            detector = AdaptiveAnomalyDetector(Path(folder) / "baseline.json")
            engine = MaritimeRiskEngine(detector)
            reading = SensorSimulator("TEST-1", "normal").read()
            assessment, events = engine.analyse(reading)
            self.assertEqual(events, [])
            self.assertEqual(assessment["risk_level"], "LOW")

    def test_offline_outbox_retries_pending_events(self):
        with tempfile.TemporaryDirectory() as folder:
            store = EdgeStore(Path(folder) / "outbox.db")
            payload = {"event_id": "event-1", "sensor_data": {"water_level_mm": 600}}
            store.enqueue(payload)
            self.assertEqual(store.counts(), {"stored": 1, "pending": 1})
            self.assertEqual(store.pending()[0]["payload"], payload)
            store.mark_delivered("event-1")
            self.assertEqual(store.counts(), {"stored": 1, "pending": 0})


if __name__ == "__main__":
    unittest.main()
