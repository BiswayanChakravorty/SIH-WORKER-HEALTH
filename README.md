# MineGuard AI — IoT Mine Worker Health & Gas Hazard Safety System (SIH Edition)

An intelligent, real-time IoT safety ecosystem built for underground mine workers. Connects wearable smart wristbands and atmospheric gas sensor arrays to an automated control gateway providing **instantaneous multi-tier gas hazard alarms**, **vital signs anomaly detection**, and **predictive AI health & fatigue forecasting**.

---

## 🌟 Key Features

1. **Atmospheric Gas Hazard Alert System**:
   - Continuous multi-gas tracking: Methane ($CH_4$), Carbon Monoxide ($CO$), Oxygen ($O_2$), Hydrogen Sulfide ($H_2S$).
   - DGMS & 30 CFR §75.323 compliance: Warning at $\ge 1.0\%$, Critical Evacuation at $\ge 1.5\%$ for Methane; OSHA PEL at $50\text{ ppm}$ for CO.
   - Dual-tone synthesized audio siren + pulsating visual alarms + actionable emergency SOP protocols.

2. **Worker Biometric Health & Anomaly Triage**:
   - Real-time pulse/heart rate ($60-100\text{ bpm}$), blood oxygen ($SpO_2 \ge 95\%$), respiratory rate ($12-20\text{ brpm}$), body temperature ($36.5-37.3^\circ\text{C}$).
   - Automatic detection of Tachycardia, Hypoxia, Heat Stroke, and Worker Fall/Impact.

3. **AI Health & Fatigue Predictive Forecaster**:
   - Physiological strain and cardiac drift trend analysis.
   - Forward-looking **15-min, 30-min, and 60-min predictive fatigue chart**.
   - Safe continuous working time countdown ($T_{\text{safe}}$) and ergonomic rest recommendations.

4. **Underground Spatial Tracking & Interactive Test Bench**:
   - Multi-level mine drift map with live worker location pins.
   - 1-Click live hazard injector to demonstrate gas outbursts and cardiac spikes during hackathon presentations.

5. **Production Hardware Firmware (ESP32 / Arduino)**:
   - Ready-to-flash C++ firmware with MAX30102, DS18B20, MPU6050, MQ-4/MQ-7, and HMAC-SHA256 authenticated HTTP POST telemetry.

---

## 🚀 Quickstart (Running the Project)

### Option 1: 1-Click Startup (Windows)
Double-click `run_server.bat` or right-click `run_server.ps1` and choose **Run with PowerShell**.

### Option 2: Command Line
```powershell
cd C:\Users\Admin\.gemini\antigravity\scratch\mine-worker-safety-sih
.venv\Scripts\activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## 🧪 Running Automated Tests
```powershell
uv run --python .venv/Scripts/python.exe pytest tests/ -v
```

---

## 📁 Project Directory Structure
```
mine-worker-safety-sih/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI server, WebSockets & REST endpoints
│   │   ├── config.py             # DGMS/OSHA/CMR safety thresholds
│   │   ├── database.py           # SQLite async persistence & models
│   │   ├── schemas.py            # Pydantic validation schemas
│   │   ├── safety_engine.py      # Multi-gas & vital sign evaluator
│   │   ├── forecaster.py         # AI 15m/30m/60m predictive health forecaster
│   │   └── hardware_simulator.py # Background continuous telemetry generator
│   ├── firmware/
│   │   └── esp32_worker_band.ino # Production Arduino/ESP32 C++ firmware
│   └── requirements.txt
├── frontend/
│   ├── index.html                # Simple, mission-control dashboard UI
│   ├── app.js                    # Real-time WebSocket client, audio alarm & Chart.js
│   └── styles.css                # Industrial high-contrast command center styling
├── tests/
│   ├── test_safety_engine.py     # Gas & vital signs unit tests
│   ├── test_forecaster.py        # Fatigue & predictive forecasting tests
│   └── test_telemetry_api.py     # REST/WebSocket integration tests
├── docs/
│   ├── SIH_PROJECT_SYNOPSIS.md   # Presentation synopsis, BOM & Judge Viva Q&A
│   ├── HARDWARE_SETUP.md         # Hardware wiring diagram & sensor calibration
│   └── ARCHITECTURE.md           # Technical architecture & JSON API specs
├── run_server.bat                # Windows 1-click launcher
├── run_server.ps1                # PowerShell launcher
└── README.md
```
