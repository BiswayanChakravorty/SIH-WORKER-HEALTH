# MineGuard AI — System Architecture & Data Protocol Specification

This document details the software architecture, REST/WebSocket APIs, security authentication mechanisms, and SQLite database schema.

---

## 1. System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                        PHYSICAL HARDWARE WEARABLE LAYER                           |
|  ESP32 MCU | MAX30102 (HR/SpO2) | MQ-4 (CH4) | MQ-7 (CO) | DS18B20 | MPU6050       |
+-----------------------------------------+-----------------------------------------+
                                          |
                        HTTP POST / WebSocket (JSON + HMAC-SHA256)
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        FASTAPI SAFETY ENGINE & GATEWAY                            |
|                                                                                   |
|  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐  |
|  │  Ingestion & HMAC     │  │   Multi-Gas Safety    │  │  Vital Sign Anomaly   │  |
|  │  Signature Validator  │  │  Evaluator (DGMS/OSHA)│  │  Classifier & Triage  │  |
|  └──────────┬────────────┘  └──────────┬────────────┘  └──────────┬────────────┘  |
|             │                          │                          │               |
|             └──────────────────────────┼──────────────────────────┘               |
|                                        ▼                                          |
|                     ┌─────────────────────────────────────┐                       |
|                     │   AI Health & Fatigue Forecaster    │                       |
|                     │  (15m/30m/60m Predictive Horizon)   │                       |
|                     └──────────────────┬──────────────────┘                       |
|                                        ▼                                          |
|                     ┌─────────────────────────────────────┐                       |
|                     │  SQLite Database Persistence Layer  │                       |
|                     └──────────────────┬──────────────────┘                       |
+----------------------------------------┼------------------------------------------+
                                         │
                        WebSocket Broadcast (`/ws/live`)
                                         │
                                         v
+-----------------------------------------------------------------------------------+
|                    MISSION-CONTROL FRONTEND DASHBOARD (SPA)                       |
|  - Real-Time Gas Level Meters & Threshold Bars                                    |
|  - Biometric Vitals (Heart Rate BPM, SpO2 %, Temp °C, Resp)                       |
|  - Web Audio Synthesized Dual-Tone Emergency Siren                                |
|  - AI Health & Fatigue Predictive Line Chart (Chart.js)                           |
|  - Underground Mine Schematic & Worker Pinning                                    |
|  - 1-Click Interactive Test Bench for Jury Presentations                          |
|  - Regulatory Compliance Matrix (DGMS / OSHA / 30 CFR §75.323)                    |
+-----------------------------------------------------------------------------------+
```

---

## 2. Telemetry JSON Protocol Specification

### Request: `POST /api/telemetry/ingest`
**Header**: `X-Band-Signature: <HMAC_SHA256_HEX_STRING>` (Optional in dev mode, required in production)

```json
{
  "workerId": "MW-0742",
  "bandId": "WHB-042",
  "sequence": 142,
  "timestamp": 1700000120,
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

### Response: `200 OK`
```json
{
  "status": "success",
  "workerId": "MW-0742",
  "mineZone": "North Drift 04 (L-220m)",
  "telemetry": { ... },
  "gasSafety": {
    "overallLevel": "safe",
    "sirenRequired": false,
    "hazards": [],
    "hazardSummary": "Mine atmospheric readings stable.",
    "evacuationRequired": false,
    "recommendedSOP": "Normal operations: Continuous automated telemetry monitoring active."
  },
  "healthSafety": {
    "overallLevel": "normal",
    "alarmRequired": false,
    "anomalies": [],
    "cardiacStrain": "Resting / Nominal",
    "hypoxiaRisk": "None (Optimal)",
    "thermalStress": "Comfortable",
    "fallAlert": false
  },
  "healthForecast": {
    "workerId": "MW-0742",
    "fatigueScorePct": 18.5,
    "fatigueRiskLevel": "LOW",
    "estimatedSafeMinutesRemaining": 180,
    "cardiacDriftRateBpmPerHour": 0.5,
    "thermalAccumulationIndex": 4.0,
    "restRecommendation": "Optimal energy: Worker physiological parameters are stable.",
    "timeline": [
      { "minutesAhead": 15, "predictedHeartRate": 74.5, "predictedFatigueScore": 19.2, "predictedSpo2": 98.1, "riskLevel": "LOW" },
      { "minutesAhead": 30, "predictedHeartRate": 75.0, "predictedFatigueScore": 20.0, "predictedSpo2": 98.0, "riskLevel": "LOW" },
      { "minutesAhead": 60, "predictedHeartRate": 76.2, "predictedFatigueScore": 21.8, "predictedSpo2": 97.9, "riskLevel": "LOW" }
    ],
    "generatedAt": 1700000120
  },
  "systemLevel": "SAFE",
  "serverTimestamp": 1700000120
}
```
