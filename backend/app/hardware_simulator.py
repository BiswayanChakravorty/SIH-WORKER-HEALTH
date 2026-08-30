"""Hardware Simulator & Telemetry Generator: Simulates live ESP32 wearable bands and handles hazard injection."""
from __future__ import annotations
import random
import time
from typing import Dict, Any, Optional

class SimulatorState:
    def __init__(self):
        self.active_scenario: str = "NORMAL"
        self.sequence_counters: Dict[str, int] = {}
        self.override_data: Optional[Dict[str, float]] = None
        
        # Baselines per worker
        self.baselines = {
            "MW-0742": {
                "name": "Arjun Singh",
                "bandId": "WHB-042",
                "zone": "North Drift 04 (L-220m)",
                "hr": 74.0,
                "resp": 15.0,
                "temp": 36.8,
                "spo2": 98.2,
                "o2": 20.9,
                "ch4": 0.08,
                "co": 4.5,
                "h2s": 0.0,
                "battery": 94
            },
            "MW-0743": {
                "name": "Rajesh Kumar",
                "bandId": "WHB-043",
                "zone": "East Return Air Course (L-180m)",
                "hr": 78.0,
                "resp": 16.0,
                "temp": 36.9,
                "spo2": 97.8,
                "o2": 20.7,
                "ch4": 0.15,
                "co": 8.0,
                "h2s": 0.2,
                "battery": 89
            },
            "MW-0744": {
                "name": "Sunita Soren",
                "bandId": "WHB-044",
                "zone": "South Stope 02 (L-350m)",
                "hr": 82.0,
                "resp": 17.0,
                "temp": 37.1,
                "spo2": 98.0,
                "o2": 20.8,
                "ch4": 0.05,
                "co": 3.0,
                "h2s": 0.0,
                "battery": 96
            },
            "MW-0745": {
                "name": "Mohammed Irfan",
                "bandId": "WHB-045",
                "zone": "Main Incline Conveyor (L-120m)",
                "hr": 71.0,
                "resp": 14.0,
                "temp": 36.7,
                "spo2": 99.0,
                "o2": 20.9,
                "ch4": 0.02,
                "co": 2.0,
                "h2s": 0.0,
                "battery": 82
            }
        }

    def set_scenario(self, scenario: str, custom_overrides: Optional[Dict[str, float]] = None):
        self.active_scenario = scenario.upper()
        self.override_data = custom_overrides

    def generate_telemetry(self, worker_id: str = "MW-0742") -> Dict[str, Any]:
        if worker_id not in self.baselines:
            worker_id = "MW-0742"
            
        base = self.baselines[worker_id]
        seq = self.sequence_counters.get(worker_id, 100) + 1
        self.sequence_counters[worker_id] = seq
        
        # Micro-jitter for biological realism
        hr_jitter = random.uniform(-1.5, 1.5)
        resp_jitter = random.uniform(-0.5, 0.5)
        temp_jitter = random.uniform(-0.05, 0.05)
        spo2_jitter = random.uniform(-0.2, 0.2)
        gas_jitter = random.uniform(-0.02, 0.02)
        
        hr = base["hr"] + hr_jitter
        resp = base["resp"] + resp_jitter
        temp = base["temp"] + temp_jitter
        spo2 = base["spo2"] + spo2_jitter
        o2 = base["o2"] + gas_jitter
        ch4 = max(0.0, base["ch4"] + gas_jitter * 0.1)
        co = max(0.0, base["co"] + random.uniform(-0.5, 0.5))
        h2s = max(0.0, base["h2s"])
        fall = False
        sos = False

        # Apply active scenario transformations
        scen = self.active_scenario
        if scen == "METHANE_SPIKE" and worker_id == "MW-0742":
            ch4 = 2.18 + random.uniform(-0.05, 0.08)  # Critical evacuation >= 1.5%
            co = 18.0 + random.uniform(-1.0, 1.0)
            hr = 108.0 + random.uniform(-2.0, 3.0)   # Heart rate rises due to adrenaline
            resp = 22.0 + random.uniform(-1.0, 1.0)
        elif scen == "O2_DROP" and worker_id == "MW-0742":
            o2 = 16.4 + random.uniform(-0.2, 0.2)    # Critical hypoxia < 18%
            spo2 = 86.5 + random.uniform(-0.5, 0.5)  # Severe hypoxia
            resp = 28.0 + random.uniform(-1.0, 1.0)  # Heavy panting
            hr = 126.0 + random.uniform(-2.0, 2.0)
        elif scen == "CO_LEAK" and worker_id == "MW-0742":
            co = 74.5 + random.uniform(-2.0, 3.0)    # Exceeds 50 ppm PEL
            ch4 = 0.45
            hr = 114.0 + random.uniform(-2.0, 2.0)
            temp = 37.6 + random.uniform(-0.1, 0.1)
        elif scen == "CARDIAC_SPIKE" and worker_id == "MW-0742":
            hr = 152.0 + random.uniform(-3.0, 4.0)   # Severe Tachycardia
            resp = 29.0 + random.uniform(-1.0, 1.0)
            spo2 = 90.2 + random.uniform(-0.5, 0.5)
            temp = 38.9 + random.uniform(-0.1, 0.1)  # Hyperthermia / Heat stroke
        elif scen == "FALL_ALARM" and worker_id == "MW-0742":
            fall = True
            hr = 54.0 + random.uniform(-2.0, 2.0)    # Low pulse post-shock
            resp = 9.0 + random.uniform(-0.5, 0.5)
        elif scen == "SOS_PANIC" and worker_id == "MW-0742":
            sos = True
            hr = 132.0 + random.uniform(-2.0, 2.0)
            resp = 25.0 + random.uniform(-1.0, 1.0)

        # Apply any explicit custom overrides from the test bench UI
        if self.override_data:
            if "heartRateBpm" in self.override_data: hr = float(self.override_data["heartRateBpm"])
            if "respiratoryRateBrpm" in self.override_data: resp = float(self.override_data["respiratoryRateBrpm"])
            if "bodyTemperatureC" in self.override_data: temp = float(self.override_data["bodyTemperatureC"])
            if "spo2Percent" in self.override_data: spo2 = float(self.override_data["spo2Percent"])
            if "ambientOxygenPercent" in self.override_data: o2 = float(self.override_data["ambientOxygenPercent"])
            if "methanePercent" in self.override_data: ch4 = float(self.override_data["methanePercent"])
            if "carbonMonoxidePpm" in self.override_data: co = float(self.override_data["carbonMonoxidePpm"])
            if "hydrogenSulfidePpm" in self.override_data: h2s = float(self.override_data["hydrogenSulfidePpm"])

        return {
            "workerId": worker_id,
            "bandId": base["bandId"],
            "sequence": seq,
            "timestamp": int(time.time()),
            "heartRateBpm": round(hr, 1),
            "respiratoryRateBrpm": round(resp, 1),
            "bodyTemperatureC": round(temp, 1),
            "spo2Percent": round(spo2, 1),
            "ambientOxygenPercent": round(o2, 1),
            "methanePercent": round(ch4, 2),
            "carbonMonoxidePpm": round(co, 1),
            "hydrogenSulfidePpm": round(h2s, 1),
            "fallDetected": fall,
            "batteryPct": base["battery"],
            "signalStrengthRssi": random.randint(-68, -58),
            "sosTriggered": sos,
            "mineZone": base["zone"]
        }

simulator = SimulatorState()
