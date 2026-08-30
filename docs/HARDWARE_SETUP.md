# Hardware Setup & Wiring Guide (ESP32 Smart Safety Band)

This document provides complete instructions for wiring, calibrating, and flashing the ESP32 wearable wristband and atmospheric sensor node.

---

## 1. Circuit Pin Connections

### A. I2C Bus Devices (MAX30102 & MPU6050)
Both the MAX30102 pulse oximeter and MPU6050 6-axis accelerometer share the ESP32 hardware $I^2C$ bus:

| Sensor Pin | ESP32 Pin | Notes |
|---|---|---|
| **VCC** | 3.3V / 5V | MAX30102 operates on 3.3V; MPU6050 has onboard regulator |
| **GND** | GND | Common ground |
| **SDA** | GPIO 21 | $I^2C$ Data line |
| **SCL** | GPIO 22 | $I^2C$ Clock line |

### B. DS18B20 Temperature Sensor (1-Wire)
| DS18B20 Pin | ESP32 Pin | Notes |
|---|---|---|
| **VDD (Red)** | 3.3V | Power |
| **GND (Black)** | GND | Ground |
| **DATA (Yellow)** | GPIO 4 | Place a 4.7kΩ pull-up resistor between DATA and 3.3V |

### C. MQ-4 (Methane) & MQ-7 (Carbon Monoxide) Gas Sensors
| Gas Sensor Pin | ESP32 Pin | Notes |
|---|---|---|
| **VCC** | 5V | Heater circuit requires 5V |
| **GND** | GND | Common ground |
| **AOUT (MQ-4)** | GPIO 34 (ADC1_CH6) | Analog input for Methane |
| **AOUT (MQ-7)** | GPIO 35 (ADC1_CH7) | Analog input for Carbon Monoxide |

### D. Actuators & SOS Button
| Component | ESP32 Pin | Notes |
|---|---|---|
| **Piezo Buzzer (+)** | GPIO 18 | Connect (-) to GND |
| **High-Intensity LED (+)** | GPIO 19 | Use a 220Ω current limiting resistor to GND |
| **SOS Push Button** | GPIO 15 | Active LOW with internal pull-up |

---

## 2. Arduino IDE Setup & Flashing

1. Install Arduino IDE (v2.0+).
2. Add ESP32 Board Package:
   - Go to `Preferences` $\to$ `Additional Boards Manager URLs` $\to$ Add:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. Install required libraries via `Tools` $\to$ `Manage Libraries...`:
   - `ArduinoJson` by Benoit Blanchon (v6.21+)
   - `OneWire` by Paul Stoffregen
   - `DallasTemperature` by Miles Burton
   - `SparkFun MAX3010x Pulse and Proximity Sensor Library`
   - `Adafruit MPU6050`
4. Open [esp32_worker_band.ino](../backend/firmware/esp32_worker_band.ino).
5. Update WiFi SSID and Central Gateway IP address:
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_NAME";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* GATEWAY_INGEST_URL = "http://<YOUR_PC_IP>:8000/api/telemetry/ingest";
   ```
6. Select Board: `ESP32 Dev Module`, choose your COM port, and click **Upload**.

---

## 3. Gas Sensor Calibration Procedure

1. **Preheat Period**: MQ-series sensors require a 24-48 hour preheating period for the internal tin dioxide ($SnO_2$) heating element to stabilize.
2. **Clean Air Baseline**: In clean atmospheric air ($20.9\% O_2$, $0\% CH_4$, $0\text{ ppm } CO$), adjust the onboard trimmer potentiometer until the analog voltage output sits at $\approx 0.4\text{V} - 0.6\text{V}$.
3. **Firmware Scaling**: The firmware automatically maps the ADC scale ($0 - 4095$) to the calibrated percentage and PPM curves.
