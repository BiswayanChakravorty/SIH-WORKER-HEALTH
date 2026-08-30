"""Unit tests for AI predictive health & fatigue forecasting."""
import pytest
from backend.app.forecaster import calculate_fatigue_score, forecast_worker_health

def test_nominal_fatigue_score():
    score = calculate_fatigue_score(
        hr=72.0,
        resp=14.0,
        temp=36.8,
        spo2=98.5,
        ambient_o2=20.9
    )
    assert 0.0 <= score <= 25.0

def test_high_stress_fatigue_score():
    score = calculate_fatigue_score(
        hr=148.0,
        resp=28.0,
        temp=38.8,
        spo2=87.0,
        ambient_o2=17.0
    )
    assert score >= 75.0

def test_forecast_horizons():
    current_tel = {
        "heartRateBpm": 85.0,
        "respiratoryRateBrpm": 18.0,
        "bodyTemperatureC": 37.2,
        "spo2Percent": 97.0,
        "ambientOxygenPercent": 20.8
    }
    res = forecast_worker_health("MW-TEST-01", current_tel)
    assert res.workerId == "MW-TEST-01"
    assert len(res.timeline) == 3
    assert res.timeline[0].minutesAhead == 15
    assert res.timeline[1].minutesAhead == 30
    assert res.timeline[2].minutesAhead == 60
    assert res.estimatedSafeMinutesRemaining > 0
    assert len(res.restRecommendation) > 0
