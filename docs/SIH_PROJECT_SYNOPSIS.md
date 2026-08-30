# Smart India Hackathon (SIH) — Project Synopsis & Pitch Guide

## 1. Project Title
**MineGuard AI: IoT-Enabled Intelligent Mine Worker Health & Atmospheric Gas Safety System with Predictive Fatigue Forecasting**

---

## 2. Problem Statement & Background
Underground mining is one of the most hazardous work environments globally. Underground workers operate hundreds of meters below the surface where they face two lethal, often invisible threats:
1. **Atmospheric Gas Hazards**:
   - Explosive Methane ($CH_4$) accumulation leading to catastrophic explosions.
   - Toxic Carbon Monoxide ($CO$) from smoldering coal and diesel machinery.
   - Oxygen-deficient pockets ($O_2 < 18\%$) causing rapid asphyxiation.
   - Hydrogen Sulfide ($H_2S$) neurotoxin gas.
2. **Physiological & Heat Strain**:
   - Severe cardiac overload (Tachycardia $> 135\text{ bpm}$) caused by intense physical labor in high humidity.
   - Heat exhaustion / Hyperthermia ($> 38.6^\circ\text{C}$).
   - Sudden falls, rockfalls, or collapse in isolated drifts where emergency help is delayed.

**The Failure of Existing Solutions**:
Current mining setups rely on bulky, static wall-mounted gas detectors with blind spots, or manual shift logging without continuous biometric tracking or real-time predictive forecasting.

---

## 3. Our Solution & Core Innovations (USPs)

```
       [ Wearable ESP32 Smart Band ]                     [ Atmospheric Sensors ]
   (MAX30102, DS18B20, MPU6050, SOS Button)            (MQ-4, MQ-7, O2 Electrochemical)
                          │                                           │
                          └───────────────────┬───────────────────────┘
                                              │ Signed HMAC-SHA256 Telemetry (WiFi / LoRa)
                                              ▼
                    +───────────────────────────────────────────────────+
                    |           FASTAPI INTELLIGENT GATEWAY             |
                    |  - DGMS & 30 CFR §75.323 Multi-Gas Evaluator     |
                    |  - Biometric Anomaly Detection (Tachycardia)      |
                    |  - AI Health & Fatigue Predictive Forecaster      |
                    +─────────────────────────┬─────────────────────────+
                                              │ Real-Time WebSocket Streaming
                                              ▼
                    +───────────────────────────────────────────────────+
                    |             MISSION-CONTROL DASHBOARD             |
                    |  - Instant Multi-Tier Gas Alert & Audio Siren     |
                    |  - Live Vital Signs & ECG Pulse Monitoring        |
                    |  - 15m / 30m / 60m Health Fatigue Trend Graph     |
                    |  - Underground Mine Spatial Map & Worker Pins     |
                    |  - 1-Click SIH Live Hardware Test Bench           |
                    +───────────────────────────────────────────────────+
```

### Key Unique Selling Propositions (USPs):
1. **Dual-Pillar Safety (Environment + Biometrics)**:
   - Evaluates both the ambient mine atmosphere and the worker’s personal physiological vitals simultaneously.
2. **AI Health & Fatigue Predictive Forecaster**:
   - Projects worker cardiovascular strain, oxygen depletion, and thermal fatigue **15, 30, and 60 minutes into the future** to prescribe preventive hydration and rest before collapse occurs.
3. **Local Fail-Safe + Gateway Redundancy**:
   - The ESP32 wristband computes local alarms independently on the microcontroller (piezo buzzer & warning LED) in case of subterranean network disconnection, while the cloud/gateway synchronizes historical telemetry and control-room SOP alerts.
4. **Authoritative Mining Regulatory Compliance**:
   - Built directly against **Directorate General of Mines Safety (DGMS)**, **30 CFR §75.323**, **CMR 2017**, and **OSHA Table Z-1** standards.

---

## 4. Hardware Bill of Materials (BOM)

| Component | Purpose | Interface / Pin |
|---|---|---|
| **ESP32 Dev Module** | Core microcontroller with WiFi & Bluetooth | Central MCU |
| **MAX30102** | High-precision Heart Rate (Pulse) & $SpO_2$ Blood Oxygen | $I^2C$ (SDA: GPIO 21, SCL: GPIO 22) |
| **DS18B20** | Waterproof Digital Body/Skin Temperature | 1-Wire (GPIO 4 with 4.7kΩ pull-up) |
| **MPU6050** | 6-Axis Accelerometer & Gyroscope (Fall / Impact detection) | $I^2C$ (SDA: GPIO 21, SCL: GPIO 22) |
| **MQ-4 Gas Sensor** | Methane ($CH_4$) & Natural Gas concentration | Analog ADC (GPIO 34) |
| **MQ-7 Gas Sensor** | Carbon Monoxide ($CO$) detection | Analog ADC (GPIO 35) |
| **Piezo Buzzer & LED** | Local audible & visual hazard alarm | GPIO 18 & GPIO 19 |
| **Push Button** | Emergency SOS Panic Dispatch | GPIO 15 (Interrupt) |
| **3.7V 1200mAh LiPo** | Compact wearable power supply | TP4056 charging module |

---

## 5. Potential Judge Viva Q&A (Be Prepared!)

### Q1: How does your system operate if WiFi or connectivity is lost underground?
**Answer**: "Our architecture employs an **Edge-First Local Fail-Safe Design**. The ESP32 firmware evaluates gas limits and heart rate thresholds on the edge inside the microcontroller. If methane exceeds 1.5% or a fall is detected, the wristband sounds an instantaneous onboard 85dB piezo buzzer and illuminates high-intensity LEDs immediately, regardless of connectivity. When the worker moves within range of a mesh node, all buffered telemetry is synced to the control room gateway via authenticated REST/WebSockets."

### Q2: How does the AI Health & Fatigue Forecaster work?
**Answer**: "The forecaster uses time-series physiological modeling combining **cardiac drift velocity ($BPM/hr$)**, respiratory strain, thermal accumulation index, and oxygenation deficit. Using exponential smoothing and trend regression, it predicts the worker's fatigue index ($0-100\%$) and cardiovascular strain over $+15$, $+30$, and $+60$ minute horizons, calculating the exact safe continuous work minutes remaining ($T_{\text{safe}}$) to recommend ergonomic rest before heat stroke or cardiac arrest happens."

### Q3: What safety standards did you follow?
**Answer**: "We strictly adhered to:
- **30 CFR §75.323 & CMR 2017**: Methane warning at $\ge 1.0\%$, mandatory withdrawal at $\ge 1.5\%$.
- **OSHA 29 CFR 1910.134**: Minimum ambient oxygen baseline of $19.5\%$ and emergency threshold at $18.0\%$.
- **OSHA Table Z-1**: 8-hour Permissible Exposure Limit (PEL) for Carbon Monoxide at $50\text{ ppm}$.
- **MedlinePlus & NIOSH**: Vital signs and occupational heat stress baselines."
