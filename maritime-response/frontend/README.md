cat > README.md <<'EOF'
# 🚢 Maritime Safety Platform

A real-time maritime safety and vessel monitoring platform that combines an edge sensing agent, MQTT communication, a FastAPI backend, PostgreSQL storage, and a Next.js monitoring dashboard.

The platform collects vessel and safety data at the edge, sends it through MQTT, processes and stores it in the backend, and presents live vessel positions, AIS traffic, incidents, alerts, weather information, and safety conditions through a web dashboard.

---

## 🎯 Project Objectives

- Monitor maritime vessels in real time.
- Collect sensor data from an edge device/agent.
- Simulate and process AIS vessel information.
- Detect maritime safety conditions and incidents.
- Communicate edge data using MQTT.
- Persist vessel and incident information in PostgreSQL.
- Provide REST APIs through FastAPI.
- Display live vessel positions on an interactive maritime map.
- Provide real-time safety alerts and incident information.
- Provide a centralized dashboard for maritime monitoring.

---

## 🏗️ System Architecture

```text
┌──────────────────────────────────────┐
│             EDGE AGENT               │
│                                      │
│ GPS • IMU • Fire • Water • Engine    │
│ Panic • AIS                           │
│                                      │
│ AI Anomaly Detection                 │
│ Confidence Scoring                   │
│ Alert Management                     │
└──────────────────┬───────────────────┘
                   │
                   │ MQTT
                   ▼
┌──────────────────────────────────────┐
│          FASTAPI BACKEND             │
│                                      │
│ MQTT Subscriber                      │
│ Vessel API                           │
│ Incident API                         │
│ Authentication                       │
│ SQLAlchemy                           │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             PostgreSQL               │
│                                      │
│ Vessels                              │
│ Incidents                            │
│ Users                                │
└──────────────────┬───────────────────┘
                   │
                   │ REST API
                   ▼
┌──────────────────────────────────────┐
│          NEXT.JS DASHBOARD           │
│                                      │
│ KPI Monitoring                       │
│ Vessel Overview                      │
│ Safety Alerts                        │
│ Weather                              │
│ AIS Tracking                         │
│ Interactive Maritime Map             │
└──────────────────────────────────────┘