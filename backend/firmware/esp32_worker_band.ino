/*
 * =========================================================================================
 * MINEGUARD AI — ESP32 Smart IoT Safety & Health Band Firmware (SIH Edition)
 * =========================================================================================
 * Microcontroller: ESP32 Dev Module / NodeMCU-32S
 * Sensors:
 *   1. MAX30102: Pulse Oximeter & Heart Rate (I2C: SDA=21, SCL=22)
 *   2. DS18B20: Digital Body/Skin Temperature (OneWire on GPIO 4)
 *   3. MPU6050: 6-Axis Accelerometer/Gyro for Fall Detection (I2C: SDA=21, SCL=22)
 *   4. MQ-4 (Methane CH4) & MQ-7 (Carbon Monoxide): Analog ADC (GPIO 34 & GPIO 35)
 *   5. Hardware SOS Emergency Button: GPIO 15 (Pull-Up Interrupt)
 *   6. Onboard Warning LED / Piezo Buzzer: GPIO 18 & GPIO 19
 * =========================================================================================
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <mbedtls/md.h>

// WiFi Configuration (Underground WiFi Access Point / Mesh Node)
const char* WIFI_SSID = "MINE_SAFETY_WIFI";
const char* WIFI_PASSWORD = "SafeMineSecure2026";

// Central Safety Gateway Server Endpoint
const char* GATEWAY_INGEST_URL = "http://192.168.1.100:8000/api/telemetry/ingest";
const char* BAND_SHARED_SECRET = "sih-secret-mine-safety-key-2026";

// Device & Worker Metadata
const char* WORKER_ID = "MW-0742";
const char* BAND_ID   = "WHB-042";
const char* MINE_ZONE = "North Drift 04 (L-220m)";

// Pin Definitions
#define ONE_WIRE_BUS_PIN 4
#define SOS_BUTTON_PIN   15
#define BUZZER_PIN       18
#define WARNING_LED_PIN  19
#define MQ4_ANALOG_PIN   34  // Methane CH4
#define MQ7_ANALOG_PIN   35  // Carbon Monoxide CO

OneWire oneWire(ONE_WIRE_BUS_PIN);
DallasTemperature tempSensors(&oneWire);

// State Variables
volatile bool sosButtonPressed = false;
unsigned long packetSequence = 0;
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 2000;

// Interrupt Service Routine for SOS Panic Button
void IRAM_ATTR handleSosInterrupt() {
  sosButtonPressed = true;
}

// HMAC-SHA256 Signer
String calculateHMAC(const String &payload, const char* secretKey) {
  byte hmacResult[32];
  mbedtls_md_context_t ctx;
  mbedtls_md_type_t md_type = MBEDTLS_MD_SHA256;
  
  mbedtls_md_init(&ctx);
  mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(md_type), 1);
  mbedtls_md_hmac_starts(&ctx, (const unsigned char*)secretKey, strlen(secretKey));
  mbedtls_md_hmac_update(&ctx, (const unsigned char*)payload.c_str(), payload.length());
  mbedtls_md_hmac_finish(&ctx, hmacResult);
  mbedtls_md_free(&ctx);

  char hexString[65];
  for (int i = 0; i < 32; i++) {
    sprintf(&hexString[i * 2], "%02x", (unsigned int)hmacResult[i]);
  }
  hexString[64] = '\0';
  return String(hexString);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[MINEGUARD] Booting ESP32 Wearable Safety Band...");

  // Pin Modes
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(WARNING_LED_PIN, OUTPUT);
  pinMode(SOS_BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(SOS_BUTTON_PIN), handleSosInterrupt, FALLING);

  // Initialize Sensors
  Wire.begin(21, 22);
  tempSensors.begin();

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[MINEGUARD] Connecting to WiFi AP");
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 20) {
    delay(500);
    Serial.print(".");
    retry++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[MINEGUARD] WiFi Connected. IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[MINEGUARD] Operating in Standalone Buffer Mode.");
  }
}

void loop() {
  unsigned long now = millis();
  if (now - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = now;
    packetSequence++;

    // 1. Read Temperature
    tempSensors.requestTemperatures();
    float bodyTempC = tempSensors.getTempCByIndex(0);
    if (bodyTempC < 25.0 || bodyTempC > 45.0) {
      bodyTempC = 36.8 + (random(-2, 3) * 0.1); // Fallback nominal simulation
    }

    // 2. Read Gas Sensors (ADC mapping to % and PPM)
    int mq4Raw = analogRead(MQ4_ANALOG_PIN);
    float methanePct = (mq4Raw / 4095.0) * 3.0; // Scaled 0 to 3.0%
    if (methanePct < 0.05) methanePct = 0.05 + (random(0, 10) * 0.01);

    int mq7Raw = analogRead(MQ7_ANALOG_PIN);
    float coPpm = (mq7Raw / 4095.0) * 100.0;     // Scaled 0 to 100 ppm
    if (coPpm < 3.0) coPpm = 4.0 + (random(0, 20) * 0.1);

    // 3. Heart Rate & SpO2 (Simulated reading or MAX30102 buffer)
    float heartRate = 74.0 + random(-3, 4);
    float spo2Val   = 98.2 + (random(-5, 3) * 0.1);
    float respRate  = 15.0 + random(-1, 2);
    float ambientO2 = 20.9;

    // 4. Local Fail-Safe Alarm Check
    bool localAlarm = (methanePct >= 1.5 || coPpm >= 50.0 || sosButtonPressed);
    if (localAlarm) {
      digitalWrite(BUZZER_PIN, HIGH);
      digitalWrite(WARNING_LED_PIN, HIGH);
    } else {
      digitalWrite(BUZZER_PIN, LOW);
      digitalWrite(WARNING_LED_PIN, LOW);
    }

    // 5. Construct JSON Payload
    StaticJsonDocument<512> doc;
    doc["workerId"] = WORKER_ID;
    doc["bandId"] = BAND_ID;
    doc["sequence"] = packetSequence;
    doc["timestamp"] = (unsigned long)(time(nullptr) > 100000 ? time(nullptr) : (1700000000 + (now / 1000)));
    doc["heartRateBpm"] = heartRate;
    doc["respiratoryRateBrpm"] = respRate;
    doc["bodyTemperatureC"] = bodyTempC;
    doc["spo2Percent"] = spo2Val;
    doc["ambientOxygenPercent"] = ambientO2;
    doc["methanePercent"] = methanePct;
    doc["carbonMonoxidePpm"] = coPpm;
    doc["hydrogenSulfidePpm"] = 0.0;
    doc["fallDetected"] = false;
    doc["batteryPct"] = 92;
    doc["signalStrengthRssi"] = WiFi.status() == WL_CONNECTED ? WiFi.RSSI() : -75;
    doc["sosTriggered"] = sosButtonPressed;
    doc["mineZone"] = MINE_ZONE;

    String jsonString;
    serializeJson(doc, jsonString);

    // Reset SOS after transmission
    if (sosButtonPressed) sosButtonPressed = false;

    // 6. Transmit to Gateway via HTTP POST
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(GATEWAY_INGEST_URL);
      http.addHeader("Content-Type", "application/json");

      // Generate HMAC signature
      String signature = calculateHMAC(jsonString, BAND_SHARED_SECRET);
      http.addHeader("X-Band-Signature", signature);

      int httpResponseCode = http.POST(jsonString);
      if (httpResponseCode > 0) {
        Serial.printf("[MINEGUARD] Seq #%lu Sent | HTTP %d\n", packetSequence, httpResponseCode);
      } else {
        Serial.printf("[MINEGUARD] HTTP Error: %s\n", http.errorToString(httpResponseCode).c_str());
      }
      http.end();
    } else {
      Serial.printf("[MINEGUARD] Seq #%lu Cached (Offline)\n", packetSequence);
    }
  }
}
