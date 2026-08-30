"""Predictive Health & Fatigue Forecaster: AI time-series projection of worker strain, fatigue, and safe work time."""
from __future__ import annotations
import time
from typing import List, Dict, Any, Optional
import numpy as np
from .schemas import HealthForecastResult, ForecastPoint

# In-memory circular telemetry history per worker for time-series forecasting
worker_telemetry_history: Dict[str, List[Dict[str, Any]]] = {}
MAX_HISTORY_POINTS = 60  # keep last 60 minutes of sampled telemetry

def record_worker_history(worker_id: str, telemetry: Dict[str, Any]):
    """Appends recent telemetry to the rolling window buffer."""
    if worker_id not in worker_telemetry_history:
        worker_telemetry_history[worker_id] = []
    
    entry = {
        "timestamp": telemetry.get("timestamp", int(time.time())),
        "heartRateBpm": float(telemetry.get("heartRateBpm", 75.0)),
        "respiratoryRateBrpm": float(telemetry.get("respiratoryRateBrpm", 15.0)),
        "bodyTemperatureC": float(telemetry.get("bodyTemperatureC", 37.0)),
        "spo2Percent": float(telemetry.get("spo2Percent", 98.0)),
        "ambientOxygenPercent": float(telemetry.get("ambientOxygenPercent", 20.9)),
    }
    
    worker_telemetry_history[worker_id].append(entry)
    if len(worker_telemetry_history[worker_id]) > MAX_HISTORY_POINTS:
        worker_telemetry_history[worker_id].pop(0)

def calculate_fatigue_score(
    hr: float,
    resp: float,
    temp: float,
    spo2: float,
    ambient_o2: float
) -> float:
    """Calculates instantaneous worker physiological fatigue score (0 to 100%)."""
    # 1. Cardiovascular load contribution (0 to 45 pts)
    # 60 bpm = 0 pts, 135+ bpm = 45 pts
    hr_norm = max(0.0, min(1.0, (hr - 60.0) / 75.0))
    hr_score = hr_norm * 45.0
    
    # 2. Respiratory strain contribution (0 to 20 pts)
    # 12 brpm = 0 pts, 28+ brpm = 20 pts
    resp_norm = max(0.0, min(1.0, (resp - 12.0) / 16.0))
    resp_score = resp_norm * 20.0
    
    # 3. Oxygenation deficit penalty (0 to 25 pts)
    # 98% SpO2 = 0 pts, 88% SpO2 = 25 pts
    spo2_deficit = max(0.0, 96.0 - spo2)
    o2_ambient_deficit = max(0.0, 20.0 - ambient_o2) * 2.0
    spo2_score = min(25.0, spo2_deficit * 3.5 + o2_ambient_deficit)
    
    # 4. Thermal accumulation stress (0 to 15 pts)
    # 36.8 C = 0 pts, 38.6+ C = 15 pts
    temp_norm = max(0.0, min(1.0, (temp - 36.8) / 1.8))
    temp_score = temp_norm * 15.0
    
    total_fatigue = min(100.0, max(0.0, hr_score + resp_score + spo2_score + temp_score))
    return round(total_fatigue, 1)

def forecast_worker_health(
    worker_id: str,
    current_telemetry: Dict[str, Any]
) -> HealthForecastResult:
    """Generates 15m, 30m, and 60m predictive forecasts for cardiac strain and fatigue."""
    record_worker_history(worker_id, current_telemetry)
    history = worker_telemetry_history.get(worker_id, [])
    
    curr_hr = float(current_telemetry.get("heartRateBpm", 76.0))
    curr_resp = float(current_telemetry.get("respiratoryRateBrpm", 15.0))
    curr_temp = float(current_telemetry.get("bodyTemperatureC", 37.0))
    curr_spo2 = float(current_telemetry.get("spo2Percent", 98.0))
    curr_o2 = float(current_telemetry.get("ambientOxygenPercent", 20.9))
    
    curr_fatigue = calculate_fatigue_score(curr_hr, curr_resp, curr_temp, curr_spo2, curr_o2)
    
    # Estimate cardiac drift slope (bpm per hour) from historical trend if available
    cardiac_drift_slope = 0.0
    if len(history) >= 4:
        hr_series = [h["heartRateBpm"] for h in history]
        x = np.arange(len(hr_series))
        slope, _ = np.polyfit(x, hr_series, 1)
        # Assuming 1 sample per minute or interval, slope per 60 min
        cardiac_drift_slope = float(slope * 60.0)
    else:
        # Default physiological drift estimation under underground working conditions
        if curr_hr > 110:
            cardiac_drift_slope = 8.5
        elif curr_hr > 90:
            cardiac_drift_slope = 3.2
        else:
            cardiac_drift_slope = 0.5
            
    cardiac_drift_slope = round(cardiac_drift_slope, 2)
    
    # Thermal load accumulation index
    thermal_index = round(max(0.0, (curr_temp - 36.5) * 10.0), 1)
    
    # Generate Forecast Points (+15m, +30m, +60m)
    timeline: List[ForecastPoint] = []
    time_horizons = [15, 30, 60]
    
    for minutes in time_horizons:
        hours_ahead = minutes / 60.0
        # Projected Heart Rate with exponential damping
        hr_delta = cardiac_drift_slope * hours_ahead
        pred_hr = round(min(180.0, max(50.0, curr_hr + hr_delta)), 1)
        
        # Projected SpO2 (decreases slightly if ambient O2 is deficient or fatigue high)
        spo2_delta = -0.8 * hours_ahead if curr_o2 < 19.5 or curr_fatigue > 60 else -0.1 * hours_ahead
        pred_spo2 = round(max(80.0, min(100.0, curr_spo2 + spo2_delta)), 1)
        
        # Projected Fatigue
        fatigue_delta = (hr_delta * 0.45) + (5.0 * hours_ahead if curr_fatigue > 50 else 2.0 * hours_ahead)
        pred_fatigue = round(min(100.0, max(0.0, curr_fatigue + fatigue_delta)), 1)
        
        # Risk level for future horizon
        if pred_fatigue >= 75.0 or pred_hr >= 135.0 or pred_spo2 < 90.0:
            risk = "CRITICAL"
        elif pred_fatigue >= 55.0 or pred_hr >= 110.0 or pred_spo2 < 93.0:
            risk = "ELEVATED"
        elif pred_fatigue >= 35.0 or pred_hr >= 95.0:
            risk = "MODERATE"
        else:
            risk = "LOW"
            
        timeline.append(ForecastPoint(
            minutesAhead=minutes,
            predictedHeartRate=pred_hr,
            predictedFatigueScore=pred_fatigue,
            predictedSpo2=pred_spo2,
            riskLevel=risk
        ))
        
    # Estimated safe working minutes remaining before mandatory rest break
    # High threshold = 80% fatigue
    if curr_fatigue >= 80.0:
        safe_mins = 0
    else:
        rate_per_min = max(0.2, (cardiac_drift_slope * 0.45 + 3.0) / 60.0)
        safe_mins = int((80.0 - curr_fatigue) / rate_per_min)
        safe_mins = max(5, min(240, safe_mins))
        
    # Risk Level & Ergonomic Recommendation
    if curr_fatigue >= 75.0:
        fatigue_level = "CRITICAL"
        recommendation = "🚨 CRITICAL FATIGUE / CARDIAC OVERLOAD: Mandate immediate 25-minute relief to Surface/Fresh Air Base."
    elif curr_fatigue >= 55.0:
        fatigue_level = "ELEVATED"
        recommendation = "⚠️ HIGH PHYSICAL STRAIN: Schedule a 15-minute hydration and rest pause within the next 20 minutes."
    elif curr_fatigue >= 35.0:
        fatigue_level = "MODERATE"
        recommendation = "ℹ️ MODERATE WORKLOAD: Shift vitals within acceptable limits. Hydrate frequently."
    else:
        fatigue_level = "LOW"
        recommendation = "✅ OPTIMAL ENERGY: Worker physiological parameters are stable and within nominal baseline."

    return HealthForecastResult(
        workerId=worker_id,
        fatigueScorePct=curr_fatigue,
        fatigueRiskLevel=fatigue_level,
        estimatedSafeMinutesRemaining=safe_mins,
        cardiacDriftRateBpmPerHour=cardiac_drift_slope,
        thermalAccumulationIndex=thermal_index,
        restRecommendation=recommendation,
        timeline=timeline,
        generatedAt=int(time.time())
    )
