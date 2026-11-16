# Maritime AI Edge Agent

This folder contains the Edge Agent for the AI-Powered Maritime Emergency Response System.

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## Run one simulated telemetry cycle

```powershell
py main.py --scenario fire --once
```

Supported scenarios are defined by the Edge Agent CLI. To run repeated cycles, omit `--once` or use `--cycles N`.

## Backend connection

Edit `config.json` and set `backend_url` to the reachable backend address, for example `http://127.0.0.1:8000/api/v1/telemetry` for a same-computer test. For a separate backend computer, replace `127.0.0.1` with that computer's LAN IP.

## Notes

- The Edge Agent stores queued telemetry in `data/edge_outbox.db` and retries delivery when the backend is reachable.
- Do not commit credentials, `.env` files, virtual environments, Python caches, or runtime database files.
- The included detector is an adaptive statistical anomaly detector combined with explicit maritime safety rules; it is not a pretrained neural network.
