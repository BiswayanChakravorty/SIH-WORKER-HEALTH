# 📡 How Hardware Data Works (Team & Judge Presentation Guide)

This guide explains step-by-step **how our IoT Hardware Wearable communicates with the Software Gateway** when live data is received.

---

## 🏗️ 1. The Complete End-to-End Data Flow

```
[ STEP 1: SENSORS ON WORKER'S WRIST ]
- MAX30102: Heartbeat (Pulse BPM)
- MQ-4: Methane Gas (CH4 %)
- MQ-7: Carbon Monoxide (CO PPM)
- MPU6050: Fall / Impact Detection
- Hardware SOS Button: Manual Panic
             │
             ▼
[ STEP 2: ESP32 MICROCONTROLLER ]
- Samples calibrated data every 1.5 seconds.
- Local Fail-Safe Check: If Methane ≥ 1.5% or SOS pressed, triggers onboard 85dB Buzzer & LED immediately (works even offline!).
- Packages sensor readings into JSON.
- Generates HMAC-SHA256 digital signature (`X-Band-Signature`) using secret key.
             │
             ▼
[ STEP 3: SUBTERRANEAN TRANSMISSION ]
- Transmits via Underground WiFi Access Point / LoRa Gateway / ESP-NOW Mesh.
- HTTP POST request to: `https://<YOUR_GATEWAY_URL>/api/telemetry/ingest`
             │
             ▼
[ STEP 4: FASTAPI BACKEND GATEWAY ]
- Authenticates HMAC signature to reject spoofed/malformed packets.
- 1) DGMS & OSHA Gas Evaluator: Compares CH4, CO, O2 against mining law limits.
- 2) Biometric Anomaly Detector: Flags Tachycardia (>110 BPM), Cardiac Distress (>138 BPM), or Falls.
- 3) AI Health & Fatigue Forecaster: Calculates cardiac drift slope and projects fatigue for +15m, +30m, and +60m.
- 4) SQLite Database: Persistently saves telemetry logs and hazard events.
             │
             ▼
[ STEP 5: REAL-TIME WEBSOCKET BROADCAST ]
- Gateway pushes live packet to all connected control room screens via `/ws/live` in < 50 milliseconds.
             │
             ▼
[ STEP 6: MISSION-CONTROL UI DISPLAY ]
- Gas cards update instantly with green/amber/red status.
- If gas is dangerous:
  * Master banner flashes red: "🚨 CRITICAL GAS HAZARD — EVACUATE!"
  * Dual-tone audio siren sounds automatically.
  * Actionable emergency SOP instructions appear on screen.
- Heartbeat card pulses and updates the predictive forecast chart.
```

---

## 📦 2. The Exact JSON Telemetry Payload

This is the exact JSON structure sent by the ESP32 hardware band every 1.5 seconds:

```json
{
  "workerId": "MW-0742",
  "bandId": "WHB-042",
  "sequence": 1045,
  "timestamp": 1788107200,
  "heartRateBpm": 78.5,
  "respiratoryRateBrpm": 16.0,
  "bodyTemperatureC": 36.9,
  "spo2Percent": 98.0,
  "ambientOxygenPercent": 20.9,
  "methanePercent": 0.08,
  "carbonMonoxidePpm": 4.5,
  "hydrogenSulfidePpm": 0.0,
  "fallDetected": false,
  "batteryPct": 94,
  "signalStrengthRssi": -62,
  "sosTriggered": false,
  "mineZone": "North Drift 04 (L-220m)"
}
```

---

## 💬 3. Clear Answers for Your Team & Hackathon Judges

### Q1: What happens if network connection is lost underground?
> **Answer**: "Our solution has a **Local Edge Fail-Safe**. The ESP32 wristband evaluates safety thresholds on the chip itself. If Methane reaches 1.5% or a fall is detected, the wristband sounds its local 85dB buzzer and LED flash on the worker's wrist immediately without needing internet. When re-entering WiFi/Mesh coverage, it synchronizes all buffered telemetry to the central database."

### Q2: How does the software identify which gas is dangerous?
> **Answer**: "The backend runs a Multi-Gas Decision Engine mapped to **Directorate General of Mines Safety (DGMS)** and **30 CFR §75.323** rules:
> - **Methane ($CH_4$)**: Warning at $\ge 1.0\%$, Critical Evacuation at $\ge 1.5\%$.
> - **Carbon Monoxide ($CO$)**: Warning at $\ge 25\text{ ppm}$, OSHA PEL Danger at $\ge 50\text{ ppm}$.
> - **Oxygen ($O_2$)**: Warning at $< 19.5\%$, Asphyxiation Danger at $< 18.0\%$.
> The software identifies the exact gas hazard and issues specific evacuation SOPs."

### Q3: How does the Heartbeat AI Forecasting work?
> **Answer**: "The forecaster calculates the **rate of cardiac drift ($BPM/\text{hr}$)** and workload exertion over time. Using time-series regression, it predicts the worker's cardiovascular strain and fatigue level **15, 30, and 60 minutes into the future**, calculating remaining safe continuous work time ($T_{\text{safe}}$) before exhaustion occurs."
