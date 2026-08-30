"""Integration tests for FastAPI REST and Ingestion API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_get_system_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "appName" in data
        assert "systemLevel" in data
        assert "activeWorkersCount" in data

@pytest.mark.asyncio
async def test_get_standards():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/standards")
        assert response.status_code == 200
        data = response.json()
        assert "atmosphericGases" in data
        assert "biometrics" in data

@pytest.mark.asyncio
async def test_telemetry_ingest_and_evaluate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "workerId": "MW-0742",
            "bandId": "WHB-042",
            "sequence": 1,
            "timestamp": 1700000000,
            "heartRateBpm": 82.0,
            "respiratoryRateBrpm": 16.0,
            "bodyTemperatureC": 36.9,
            "spo2Percent": 98.0,
            "ambientOxygenPercent": 20.9,
            "methanePercent": 0.05,
            "carbonMonoxidePpm": 4.0,
            "hydrogenSulfidePpm": 0.0,
            "fallDetected": False,
            "batteryPct": 95,
            "signalStrengthRssi": -60,
            "sosTriggered": False,
            "mineZone": "North Drift 04 (L-220m)"
        }
        response = await ac.post("/api/telemetry/ingest", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["systemLevel"] == "SAFE"
        assert "gasSafety" in data
        assert "healthSafety" in data
        assert "healthForecast" in data

@pytest.mark.asyncio
async def test_scenario_trigger():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/simulator/scenario", json={
            "scenario": "METHANE_SPIKE",
            "workerId": "MW-0742"
        })
        assert response.status_code == 200
        data = response.json()
        assert "METHANE_SPIKE" in data["message"]
        assert data["activeData"]["systemLevel"] == "CRITICAL"
