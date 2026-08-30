"""Pydantic data schemas for telemetry, safety reports, health forecasting, and worker fleet."""
from __future__ import annotations
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class TelemetryPayload(BaseModel):
    workerId: str = Field(default="MW-0742", description="Unique worker identification code")
    bandId: str = Field(default="WHB-042", description="Assigned hardware wristband MAC/ID")
    sequence: int = Field(default=1, description="Monotonically increasing packet sequence number")
    timestamp: int = Field(description="Unix epoch timestamp in seconds")
    
    # Vital signs
    heartRateBpm: float = Field(..., ge=30, le=240, description="Heart rate in beats per minute")
    respiratoryRateBrpm: float = Field(..., ge=4, le=60, description="Respiratory rate in breaths per min")
    bodyTemperatureC: float = Field(..., ge=30.0, le=45.0, description="Body/skin temperature in Celsius")
    spo2Percent: float = Field(default=98.0, ge=50.0, le=100.0, description="Blood oxygen saturation %")
    fallDetected: bool = Field(default=False, description="Tripped/Fell impact sensor flag")
    
    # Atmospheric gas concentrations
    ambientOxygenPercent: float = Field(..., ge=0.0, le=100.0, description="Ambient Oxygen %")
    methanePercent: float = Field(..., ge=0.0, le=100.0, description="Methane (CH4) % concentration")
    carbonMonoxidePpm: float = Field(..., ge=0.0, le=5000.0, description="Carbon Monoxide (CO) in PPM")
    hydrogenSulfidePpm: float = Field(default=0.0, ge=0.0, le=500.0, description="Hydrogen Sulfide (H2S) in PPM")
    
    # Context & Diagnostics
    mineZone: str = Field(default="North Drift 04 (L-220m)", description="Current underground mine zone")
    batteryPct: int = Field(default=94, ge=0, le=100, description="Wristband battery %")
    signalStrengthRssi: int = Field(default=-62, description="Wireless RSSI signal strength (dBm)")
    sosTriggered: bool = Field(default=False, description="Worker pressed physical SOS panic button")

class GasHazardItem(BaseModel):
    gas: str
    reading: float
    unit: str
    threshold: float
    severity: str  # "safe", "warning", "critical"
    message: str

class GasSafetyState(BaseModel):
    overallLevel: str  # "safe", "warning", "critical"
    sirenRequired: bool
    hazards: List[GasHazardItem]
    hazardSummary: str
    evacuationRequired: bool
    recommendedSOP: str

class HealthAnomalyItem(BaseModel):
    metric: str
    reading: float
    standard: str
    severity: str  # "normal", "caution", "danger"
    interpretation: str

class HealthSafetyState(BaseModel):
    overallLevel: str  # "normal", "caution", "danger"
    alarmRequired: bool
    anomalies: List[HealthAnomalyItem]
    cardiacStrain: str  # "Resting", "Moderate Work", "High Strain", "Critical Tachycardia"
    hypoxiaRisk: str    # "None", "Mild", "Severe"
    thermalStress: str  # "Comfortable", "Elevated", "Heat Stroke Warning"
    fallAlert: bool

class ForecastPoint(BaseModel):
    minutesAhead: int
    predictedHeartRate: float
    predictedFatigueScore: float
    predictedSpo2: float
    riskLevel: str

class HealthForecastResult(BaseModel):
    workerId: str
    fatigueScorePct: float  # 0 - 100%
    fatigueRiskLevel: str   # "LOW", "MODERATE", "ELEVATED", "CRITICAL"
    estimatedSafeMinutesRemaining: int
    cardiacDriftRateBpmPerHour: float
    thermalAccumulationIndex: float
    restRecommendation: str
    timeline: List[ForecastPoint]
    generatedAt: int

class UnifiedTelemetryResponse(BaseModel):
    status: str
    workerId: str
    mineZone: str
    telemetry: Dict[str, Any]
    gasSafety: GasSafetyState
    healthSafety: HealthSafetyState
    healthForecast: HealthForecastResult
    systemLevel: str  # "SAFE", "WARNING", "CRITICAL"
    serverTimestamp: int

class HazardInjectionRequest(BaseModel):
    scenario: str = Field(..., description="NORMAL, METHANE_SPIKE, O2_DROP, CO_LEAK, CARDIAC_SPIKE, FALL_ALARM, SOS_PANIC")
    workerId: Optional[str] = "MW-0742"
    customValues: Optional[Dict[str, float]] = None

class WorkerProfile(BaseModel):
    workerId: str
    name: str
    role: str
    bloodGroup: str
    emergencyContact: str
    assignedBandId: str
    currentZone: str
    status: str
    batteryPct: int
