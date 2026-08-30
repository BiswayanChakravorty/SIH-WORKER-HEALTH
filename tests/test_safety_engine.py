"""Unit tests for safety engine: multi-gas limits and vital sign anomaly detection."""
import pytest
from backend.app.safety_engine import evaluate_gas_hazards, evaluate_health_vitals

def test_nominal_gas_safety():
    res = evaluate_gas_hazards(ambient_o2=20.9, methane_pct=0.05, co_ppm=4.0, h2s_ppm=0.0)
    assert res.overallLevel == "safe"
    assert res.sirenRequired is False
    assert res.evacuationRequired is False
    assert len(res.hazards) == 0

def test_methane_warning_and_evacuation():
    # 1.1% CH4 -> Warning
    warn_res = evaluate_gas_hazards(ambient_o2=20.9, methane_pct=1.1, co_ppm=5.0)
    assert warn_res.overallLevel == "warning"
    assert warn_res.sirenRequired is True
    assert warn_res.evacuationRequired is False
    assert any("Methane" in h.gas and h.severity == "warning" for h in warn_res.hazards)

    # 1.6% CH4 -> Critical Evacuate (30 CFR §75.323)
    crit_res = evaluate_gas_hazards(ambient_o2=20.9, methane_pct=1.6, co_ppm=5.0)
    assert crit_res.overallLevel == "critical"
    assert crit_res.sirenRequired is True
    assert crit_res.evacuationRequired is True
    assert any("Methane" in h.gas and h.severity == "critical" for h in crit_res.hazards)

def test_oxygen_deficiency_and_hypoxia():
    # 19.0% O2 -> Warning
    warn_o2 = evaluate_gas_hazards(ambient_o2=19.0, methane_pct=0.05, co_ppm=2.0)
    assert warn_o2.overallLevel == "warning"
    assert any("Oxygen" in h.gas for h in warn_o2.hazards)

    # 16.5% O2 -> Critical Hypoxia Danger
    crit_o2 = evaluate_gas_hazards(ambient_o2=16.5, methane_pct=0.05, co_ppm=2.0)
    assert crit_o2.overallLevel == "critical"
    assert crit_o2.evacuationRequired is True

def test_carbon_monoxide_pel():
    # 60 ppm CO -> Exceeds OSHA 50 ppm PEL
    res = evaluate_gas_hazards(ambient_o2=20.9, methane_pct=0.05, co_ppm=60.0)
    assert res.overallLevel == "critical"
    assert any("Carbon Monoxide" in h.gas and h.severity == "critical" for h in res.hazards)

def test_nominal_vitals():
    res = evaluate_health_vitals(
        heart_rate=72.0,
        respiratory_rate=15.0,
        body_temp=36.8,
        spo2=98.5,
        fall_detected=False
    )
    assert res.overallLevel == "normal"
    assert res.alarmRequired is False
    assert len(res.anomalies) == 0

def test_tachycardia_and_cardiac_overload():
    res = evaluate_health_vitals(
        heart_rate=145.0,
        respiratory_rate=26.0,
        body_temp=37.2,
        spo2=96.0
    )
    assert res.overallLevel == "danger"
    assert res.cardiacStrain == "Critical Tachycardia"
    assert any(a.metric == "Heart Rate" and a.severity == "danger" for a in res.anomalies)

def test_severe_hypoxia_vital_flag():
    res = evaluate_health_vitals(
        heart_rate=95.0,
        respiratory_rate=22.0,
        body_temp=37.0,
        spo2=86.0
    )
    assert res.overallLevel == "danger"
    assert res.hypoxiaRisk == "Severe Asphyxiation Danger"

def test_heat_stroke_hyperthermia():
    res = evaluate_health_vitals(
        heart_rate=118.0,
        respiratory_rate=24.0,
        body_temp=38.9,
        spo2=96.0
    )
    assert res.overallLevel == "danger"
    assert res.thermalStress == "Heat Stroke Warning"

def test_fall_and_sos_detection():
    res_fall = evaluate_health_vitals(75.0, 15.0, 36.8, 98.0, fall_detected=True)
    assert res_fall.overallLevel == "danger"
    assert res_fall.fallAlert is True

    res_sos = evaluate_health_vitals(75.0, 15.0, 36.8, 98.0, sos_triggered=True)
    assert res_sos.overallLevel == "danger"
    assert any("SOS" in a.metric for a in res_sos.anomalies)
