"""Safety Engine: Comprehensive multi-gas hazard evaluation and vital signs anomaly detection."""
from __future__ import annotations
from typing import Dict, Any, List, Tuple
from .config import settings
from .schemas import (
    GasSafetyState, GasHazardItem,
    HealthSafetyState, HealthAnomalyItem,
    TelemetryPayload
)

def evaluate_gas_hazards(
    ambient_o2: float,
    methane_pct: float,
    co_ppm: float,
    h2s_ppm: float = 0.0
) -> GasSafetyState:
    """Evaluates all gas concentrations against DGMS, OSHA, and 30 CFR §75.323 standards."""
    hazards: List[GasHazardItem] = []
    is_critical = False
    is_warning = False
    
    # 1. Oxygen (O2) Evaluation
    if ambient_o2 < settings.O2_CRITICAL_PCT:
        is_critical = True
        hazards.append(GasHazardItem(
            gas="Oxygen (O₂)",
            reading=ambient_o2,
            unit="%",
            threshold=settings.O2_CRITICAL_PCT,
            severity="critical",
            message=f"CRITICAL HYPOXIA ({ambient_o2:.1f}%): Asphyxiation hazard below 18.0% minimum survival limit."
        ))
    elif ambient_o2 < settings.O2_DEFICIENCY_PCT:
        is_warning = True
        hazards.append(GasHazardItem(
            gas="Oxygen (O₂)",
            reading=ambient_o2,
            unit="%",
            threshold=settings.O2_DEFICIENCY_PCT,
            severity="warning",
            message=f"Oxygen Deficient ({ambient_o2:.1f}%): Below OSHA minimum atmospheric baseline (19.5%)."
        ))

    # 2. Methane (CH4) Evaluation (Underground Coal Mine 30 CFR §75.323 / CMR 2017)
    if methane_pct >= settings.METHANE_CRITICAL_PCT:
        is_critical = True
        hazards.append(GasHazardItem(
            gas="Methane (CH₄)",
            reading=methane_pct,
            unit="%",
            threshold=settings.METHANE_CRITICAL_PCT,
            severity="critical",
            message=f"CRITICAL EXPLOSIVE RISK ({methane_pct:.2f}%): Exceeds 1.5% mandatory withdrawal limit."
        ))
    elif methane_pct >= settings.METHANE_WARNING_PCT:
        is_warning = True
        hazards.append(GasHazardItem(
            gas="Methane (CH₄)",
            reading=methane_pct,
            unit="%",
            threshold=settings.METHANE_WARNING_PCT,
            severity="warning",
            message=f"Methane Warning ({methane_pct:.2f}%): Exceeds 1.0% action threshold. Inspect ventilation."
        ))

    # 3. Carbon Monoxide (CO) Evaluation (OSHA PEL & Spontaneous Combustion Indicator)
    if co_ppm >= settings.CO_CRITICAL_PPM:
        is_critical = True
        hazards.append(GasHazardItem(
            gas="Carbon Monoxide (CO)",
            reading=co_ppm,
            unit="ppm",
            threshold=settings.CO_CRITICAL_PPM,
            severity="critical",
            message=f"DANGEROUS CO TOXICITY ({co_ppm:.1f} ppm): Exceeds 50 ppm 8-hr Permissible Exposure Limit."
        ))
    elif co_ppm >= settings.CO_WARNING_PPM:
        is_warning = True
        hazards.append(GasHazardItem(
            gas="Carbon Monoxide (CO)",
            reading=co_ppm,
            unit="ppm",
            threshold=settings.CO_WARNING_PPM,
            severity="warning",
            message=f"Elevated CO ({co_ppm:.1f} ppm): Potential coal seam smoldering or exhaust accumulation."
        ))

    # 4. Hydrogen Sulfide (H2S) Evaluation
    if h2s_ppm >= settings.H2S_CRITICAL_PPM:
        is_critical = True
        hazards.append(GasHazardItem(
            gas="Hydrogen Sulfide (H₂S)",
            reading=h2s_ppm,
            unit="ppm",
            threshold=settings.H2S_CRITICAL_PPM,
            severity="critical",
            message=f"CRITICAL H₂S TOXICITY ({h2s_ppm:.1f} ppm): Lethal neurotoxin threshold exceeded."
        ))
    elif h2s_ppm >= settings.H2S_WARNING_PPM:
        is_warning = True
        hazards.append(GasHazardItem(
            gas="Hydrogen Sulfide (H₂S)",
            reading=h2s_ppm,
            unit="ppm",
            threshold=settings.H2S_WARNING_PPM,
            severity="warning",
            message=f"Elevated H₂S ({h2s_ppm:.1f} ppm): Rotten egg odor, respiratory irritant detected."
        ))

    # Determine overall state & SOP action
    if is_critical:
        level = "critical"
        summary = "CRITICAL ATMOSPHERIC HAZARD DETECTED! Evacuate affected mine drift."
        evacuation = True
        siren = True
        sop = (
            "🚨 EMERGENCY SOP ACTIVATED: 1) Immediately de-energize electrical power to affected shaft/drift. "
            "2) Sound underground evacuation horn. 3) Direct all workers to move upwind towards Fresh Air Base. "
            "4) Switch auxiliary ventilation fans to emergency high-flow purge mode."
        )
    elif is_warning:
        level = "warning"
        summary = "Atmospheric warning active. Gas concentration elevated above baseline."
        evacuation = False
        siren = True
        sop = (
            "⚠️ CAUTION SOP: 1) Notify Mine Ventilation Officer. 2) Inspect air brattices and ventilation curtains. "
            "3) Halt hot-work and heavy diesel equipment until levels stabilize."
        )
    else:
        level = "safe"
        summary = "Mine atmospheric readings stable. All gas levels within certified normal limits."
        evacuation = False
        siren = False
        sop = "✅ Normal operations: Continuous automated telemetry monitoring active."

    return GasSafetyState(
        overallLevel=level,
        sirenRequired=siren,
        hazards=hazards,
        hazardSummary=summary,
        evacuationRequired=evacuation,
        recommendedSOP=sop
    )

def evaluate_health_vitals(
    heart_rate: float,
    respiratory_rate: float,
    body_temp: float,
    spo2: float = 98.0,
    fall_detected: bool = False,
    sos_triggered: bool = False
) -> HealthSafetyState:
    """Evaluates biometric vitals, detects anomalies (Tachycardia, Hypoxia, Heat Stress, Fall)."""
    anomalies: List[HealthAnomalyItem] = []
    is_danger = False
    is_caution = False

    # 1. Heart Rate Evaluation
    if heart_rate >= settings.HR_CRITICAL_MAX:
        is_danger = True
        cardiac_strain = "Critical Tachycardia"
        anomalies.append(HealthAnomalyItem(
            metric="Heart Rate",
            reading=heart_rate,
            standard="60–100 bpm (Normal Rest)",
            severity="danger",
            interpretation=f"Extreme Cardiovascular Strain ({heart_rate:.0f} bpm) — High risk of cardiac distress!"
        ))
    elif heart_rate > settings.HR_WARNING_MAX:
        is_caution = True
        cardiac_strain = "High Strain"
        anomalies.append(HealthAnomalyItem(
            metric="Heart Rate",
            reading=heart_rate,
            standard="60–100 bpm (Normal Rest)",
            severity="caution",
            interpretation=f"Elevated Heart Rate ({heart_rate:.0f} bpm) — Heavy physical exertion or thermal stress."
        ))
    elif heart_rate < settings.HR_CRITICAL_MIN:
        is_danger = True
        cardiac_strain = "Severe Bradycardia"
        anomalies.append(HealthAnomalyItem(
            metric="Heart Rate",
            reading=heart_rate,
            standard="60–100 bpm (Normal Rest)",
            severity="danger",
            interpretation=f"Abnormally Low Pulse ({heart_rate:.0f} bpm) — Risk of fainting or loss of consciousness."
        ))
    elif heart_rate > 100:
        cardiac_strain = "Moderate Workload"
    else:
        cardiac_strain = "Resting / Nominal"

    # 2. Blood Oxygen SpO2 Evaluation
    if spo2 <= settings.SPO2_CRITICAL_MIN:
        is_danger = True
        hypoxia_risk = "Severe Asphyxiation Danger"
        anomalies.append(HealthAnomalyItem(
            metric="Blood Oxygen (SpO₂)",
            reading=spo2,
            standard="≥ 95% (Normal)",
            severity="danger",
            interpretation=f"Severe Hypoxia ({spo2:.1f}%) — Immediate oxygen assistance required!"
        ))
    elif spo2 <= settings.SPO2_WARNING_MIN:
        is_caution = True
        hypoxia_risk = "Mild Hypoxia"
        anomalies.append(HealthAnomalyItem(
            metric="Blood Oxygen (SpO₂)",
            reading=spo2,
            standard="≥ 95% (Normal)",
            severity="caution",
            interpretation=f"Mild Hypoxia ({spo2:.1f}%) — Potential poor ventilation or respiratory fatigue."
        ))
    else:
        hypoxia_risk = "None (Optimal)"

    # 3. Body / Skin Temperature Evaluation
    if body_temp >= settings.TEMP_CRITICAL_MAX:
        is_danger = True
        thermal_stress = "Heat Stroke Warning"
        anomalies.append(HealthAnomalyItem(
            metric="Body Temperature",
            reading=body_temp,
            standard="36.5–37.3 °C (Nominal)",
            severity="danger",
            interpretation=f"Hyperthermia / Heat Stroke Risk ({body_temp:.1f} °C) — Immediate cooldown protocol required!"
        ))
    elif body_temp >= settings.TEMP_WARNING_MAX:
        is_caution = True
        thermal_stress = "Elevated Heat Load"
        anomalies.append(HealthAnomalyItem(
            metric="Body Temperature",
            reading=body_temp,
            standard="36.5–37.3 °C (Nominal)",
            severity="caution",
            interpretation=f"Elevated Core Temp ({body_temp:.1f} °C) — Hydration and ventilation required."
        ))
    else:
        thermal_stress = "Comfortable"

    # 4. Respiratory Rate Evaluation
    if respiratory_rate >= settings.RESP_CRITICAL_MAX or respiratory_rate <= settings.RESP_CRITICAL_MIN:
        is_danger = True
        anomalies.append(HealthAnomalyItem(
            metric="Respiratory Rate",
            reading=respiratory_rate,
            standard="12–20 brpm (Nominal)",
            severity="danger",
            interpretation=f"Critical Respiratory Anomaly ({respiratory_rate:.0f} brpm) — Tachypnea / Respiratory distress."
        ))
    elif respiratory_rate > settings.RESP_WARNING_MAX:
        is_caution = True
        anomalies.append(HealthAnomalyItem(
            metric="Respiratory Rate",
            reading=respiratory_rate,
            standard="12–20 brpm (Nominal)",
            severity="caution",
            interpretation=f"High Respiratory Rate ({respiratory_rate:.0f} brpm) — Panting / High exertion."
        ))

    # 5. Fall / Impact Alert
    if fall_detected:
        is_danger = True
        anomalies.append(HealthAnomalyItem(
            metric="Motion / Fall Sensor",
            reading=1.0,
            standard="Upright / Active",
            severity="danger",
            interpretation="WORKER FALL / COLLAPSE DETECTED! High-G impact followed by lack of movement."
        ))

    # 6. SOS Panic Button
    if sos_triggered:
        is_danger = True
        anomalies.append(HealthAnomalyItem(
            metric="Manual SOS Panic",
            reading=1.0,
            standard="Standby",
            severity="danger",
            interpretation="🚨 WORKER TRIGGERED EMERGENCY SOS PANIC BUTTON! Immediate assistance requested."
        ))

    overall_level = "danger" if is_danger else "caution" if is_caution else "normal"
    
    return HealthSafetyState(
        overallLevel=overall_level,
        alarmRequired=is_danger or is_caution,
        anomalies=anomalies,
        cardiacStrain=cardiac_strain,
        hypoxiaRisk=hypoxia_risk,
        thermalStress=thermal_stress,
        fallAlert=fall_detected
    )
