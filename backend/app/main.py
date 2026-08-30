"""FastAPI Main Server: WebSocket streaming, telemetry ingestion, safety evaluation, and REST API."""
from __future__ import annotations
import asyncio
import hmac
import json
import os
import time
from contextlib import asynccontextmanager
from hashlib import sha256
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import (
    init_db, get_db, async_session_maker,
    WorkerModel, TelemetryModel, GasAlertModel, HealthIncidentModel, ZoneModel
)
from .schemas import (
    TelemetryPayload, UnifiedTelemetryResponse, HazardInjectionRequest,
    GasSafetyState, HealthSafetyState, HealthForecastResult
)
from .safety_engine import evaluate_gas_hazards, evaluate_health_vitals
from .forecaster import forecast_worker_health, record_worker_history
from .hardware_simulator import simulator

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        payload_str = json.dumps(data)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload_str)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# Background live simulator & broadcasting task
async def continuous_telemetry_loop():
    """Continuously evaluates sensor streams and broadcasts live updates every 1.5 seconds."""
    while True:
        try:
            # Generate current packet for primary worker
            telemetry_data = simulator.generate_telemetry("MW-0742")
            
            # Process & derive safety state
            result = await process_and_persist_telemetry(telemetry_data)
            
            # Broadcast to all connected control room clients
            await manager.broadcast({
                "type": "TELEMETRY_UPDATE",
                "data": result
            })
        except Exception as e:
            print(f"[Telemetry Loop Error]: {e}")
        await asyncio.sleep(1.5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing MineGuard AI Safety Engine & SQLite Database...")
    await init_db()
    # Start background telemetry generator
    task = asyncio.create_task(continuous_telemetry_loop())
    yield
    task.cancel()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_hmac_signature(raw_body: bytes, signature: Optional[str]) -> bool:
    """Verifies HMAC-SHA256 signature if present from hardware."""
    if not signature:
        return True  # Allow unauthenticated fast development mode
    secret = settings.BAND_SHARED_SECRET.encode("utf-8")
    expected = hmac.new(secret, raw_body, sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

async def process_and_persist_telemetry(data: Dict[str, Any]) -> Dict[str, Any]:
    worker_id = data.get("workerId", "MW-0742")
    
    # 1. Evaluate Gas Hazards
    gas_state = evaluate_gas_hazards(
        ambient_o2=float(data.get("ambientOxygenPercent", 20.9)),
        methane_pct=float(data.get("methanePercent", 0.0)),
        co_ppm=float(data.get("carbonMonoxidePpm", 0.0)),
        h2s_ppm=float(data.get("hydrogenSulfidePpm", 0.0))
    )
    
    # 2. Evaluate Health Vitals & Detect Anomalies
    health_state = evaluate_health_vitals(
        heart_rate=float(data.get("heartRateBpm", 75.0)),
        respiratory_rate=float(data.get("respiratoryRateBrpm", 15.0)),
        body_temp=float(data.get("bodyTemperatureC", 37.0)),
        spo2=float(data.get("spo2Percent", 98.0)),
        fall_detected=bool(data.get("fallDetected", False)),
        sos_triggered=bool(data.get("sosTriggered", False))
    )
    
    # 3. AI Predictive Health & Fatigue Forecaster
    forecast = forecast_worker_health(worker_id, data)
    
    # Determine Composite System Level
    if gas_state.overallLevel == "critical" or health_state.overallLevel == "danger":
        system_level = "CRITICAL"
    elif gas_state.overallLevel == "warning" or health_state.overallLevel == "caution":
        system_level = "WARNING"
    else:
        system_level = "SAFE"

    # Persist in Database
    try:
        async with async_session_maker() as session:
            # Update Worker status
            stmt = select(WorkerModel).where(WorkerModel.id == worker_id)
            res = await session.execute(stmt)
            worker = res.scalar_one_or_none()
            if worker:
                worker.status = system_level
                worker.battery_pct = int(data.get("batteryPct", 90))
                worker.last_seen = int(time.time())
                
            # Log telemetry packet
            log_entry = TelemetryModel(
                worker_id=worker_id,
                band_id=data.get("bandId", "WHB-042"),
                sequence=data.get("sequence", 0),
                timestamp=data.get("timestamp", int(time.time())),
                heart_rate=data.get("heartRateBpm"),
                respiratory_rate=data.get("respiratoryRateBrpm"),
                body_temp=data.get("bodyTemperatureC"),
                spo2=data.get("spo2Percent"),
                ambient_o2=data.get("ambientOxygenPercent"),
                methane_pct=data.get("methanePercent"),
                co_ppm=data.get("carbonMonoxidePpm"),
                h2s_ppm=data.get("hydrogenSulfidePpm"),
                fall_detected=data.get("fallDetected", False),
                battery_pct=data.get("batteryPct", 90),
                signal_strength=data.get("signalStrengthRssi", -60),
                sos_triggered=data.get("sosTriggered", False),
                mine_zone=data.get("mineZone", "North Drift 04 (L-220m)")
            )
            session.add(log_entry)
            
            # Log gas alerts if any
            if gas_state.overallLevel in ("warning", "critical"):
                for h in gas_state.hazards:
                    session.add(GasAlertModel(
                        worker_id=worker_id,
                        zone=data.get("mineZone", "North Drift 04 (L-220m)"),
                        gas_type=h.gas,
                        level=h.severity.upper(),
                        reading_value=h.reading,
                        threshold_value=h.threshold,
                        action_taken=gas_state.recommendedSOP
                    ))
            
            # Log health incident if dangerous
            if health_state.overallLevel in ("caution", "danger"):
                for a in health_state.anomalies:
                    session.add(HealthIncidentModel(
                        worker_id=worker_id,
                        anomaly_type=a.metric,
                        severity=a.severity.upper(),
                        heart_rate=data.get("heartRateBpm"),
                        spo2=data.get("spo2Percent"),
                        body_temp=data.get("bodyTemperatureC"),
                        notes=a.interpretation
                    ))
                    
            await session.commit()
    except Exception as db_err:
        print(f"[DB Persistence Error]: {db_err}")

    return {
        "status": "success",
        "workerId": worker_id,
        "mineZone": data.get("mineZone", "North Drift 04 (L-220m)"),
        "telemetry": data,
        "gasSafety": gas_state.model_dump(),
        "healthSafety": health_state.model_dump(),
        "healthForecast": forecast.model_dump(),
        "systemLevel": system_level,
        "serverTimestamp": int(time.time())
    }

# ==================== WEBSOCKET ENDPOINTS ====================

@app.websocket("/ws/live")
async def websocket_live_dashboard(websocket: WebSocket):
    """Real-time live telemetry and alarm stream for dashboard UI."""
    await manager.connect(websocket)
    try:
        # Send initial immediate packet
        initial_telemetry = simulator.generate_telemetry("MW-0742")
        result = await process_and_persist_telemetry(initial_telemetry)
        await websocket.send_text(json.dumps({
            "type": "INITIAL_STATE",
            "data": result
        }))
        while True:
            # Keep socket alive and handle any incoming client messages/actions
            client_msg = await websocket.receive_text()
            try:
                parsed = json.loads(client_msg)
                if parsed.get("action") == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==================== REST API ENDPOINTS ====================

@app.post("/api/telemetry/ingest")
async def ingest_hardware_telemetry(
    request: Request,
    x_band_signature: Optional[str] = Header(default=None)
):
    """Direct ingestion endpoint for physical ESP32/NodeMCU/Arduino hardware bands."""
    raw_body = await request.body()
    if not verify_hmac_signature(raw_body, x_band_signature):
        raise HTTPException(status_code=401, detail="Invalid or unauthenticated HMAC signature")
        
    try:
        payload = json.loads(raw_body)
    except Exception as err:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {err}")
        
    result = await process_and_persist_telemetry(payload)
    
    # Broadcast to all live control room dashboards
    await manager.broadcast({
        "type": "TELEMETRY_UPDATE",
        "data": result
    })
    
    return result

@app.get("/api/status")
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """Fetches high-level summary of all workers and mine zones."""
    res_workers = await db.execute(select(WorkerModel))
    workers = res_workers.scalars().all()
    
    res_zones = await db.execute(select(ZoneModel))
    zones = res_zones.scalars().all()
    
    latest_telemetry = simulator.generate_telemetry("MW-0742")
    processed = await process_and_persist_telemetry(latest_telemetry)
    
    return {
        "appName": settings.APP_NAME,
        "version": settings.VERSION,
        "systemLevel": processed["systemLevel"],
        "activeWorkersCount": len(workers),
        "workers": [
            {
                "id": w.id,
                "name": w.name,
                "role": w.role,
                "zone": w.current_zone,
                "status": w.status,
                "batteryPct": w.battery_pct,
                "lastSeen": w.last_seen
            } for w in workers
        ],
        "zones": [
            {
                "id": z.id,
                "name": z.name,
                "depthMeters": z.depth_meters,
                "ventilationStatus": z.ventilation_status,
                "hazardLevel": z.hazard_level
            } for z in zones
        ],
        "primaryWorkerTelemetry": processed
    }

@app.get("/api/workers")
async def list_workers(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkerModel))
    workers = res.scalars().all()
    return workers

@app.get("/api/workers/{worker_id}")
async def get_worker_detail(worker_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(WorkerModel).where(WorkerModel.id == worker_id))
    worker = res.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    # Get last 20 telemetry entries
    t_res = await db.execute(
        select(TelemetryModel)
        .where(TelemetryModel.worker_id == worker_id)
        .order_by(desc(TelemetryModel.timestamp))
        .limit(20)
    )
    logs = t_res.scalars().all()
    
    # Generate live forecast
    curr_tel = simulator.generate_telemetry(worker_id)
    forecast = forecast_worker_health(worker_id, curr_tel)
    
    return {
        "worker": worker,
        "currentTelemetry": curr_tel,
        "forecast": forecast,
        "recentHistory": logs
    }

@app.get("/api/zones")
async def list_zones(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ZoneModel))
    return res.scalars().all()

@app.get("/api/forecast/{worker_id}")
async def get_worker_forecast(worker_id: str = "MW-0742"):
    """Returns AI time-series predictive forecast (15m, 30m, 60m)."""
    curr = simulator.generate_telemetry(worker_id)
    forecast = forecast_worker_health(worker_id, curr)
    return forecast

@app.post("/api/simulator/scenario")
async def set_simulator_scenario(req: HazardInjectionRequest):
    """Sets active hazard simulation scenario for live demonstration."""
    simulator.set_scenario(req.scenario, req.customValues)
    # Generate immediate sample
    data = simulator.generate_telemetry(req.workerId or "MW-0742")
    result = await process_and_persist_telemetry(data)
    await manager.broadcast({
        "type": "TELEMETRY_UPDATE",
        "data": result
    })
    return {
        "message": f"Simulator scenario set to {req.scenario}",
        "activeData": result
    }

@app.post("/api/simulator/inject")
async def inject_custom_sensors(request: Request):
    """Allows manual sliders from the UI to update sensor values on the fly."""
    payload = await request.json()
    simulator.set_scenario("CUSTOM", payload)
    data = simulator.generate_telemetry(payload.get("workerId", "MW-0742"))
    result = await process_and_persist_telemetry(data)
    await manager.broadcast({
        "type": "TELEMETRY_UPDATE",
        "data": result
    })
    return result

@app.get("/api/alerts/gas")
async def get_gas_alerts(limit: int = 20, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(GasAlertModel)
        .order_by(desc(GasAlertModel.timestamp))
        .limit(limit)
    )
    return res.scalars().all()

@app.get("/api/alerts/health")
async def get_health_alerts(limit: int = 20, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HealthIncidentModel)
        .order_by(desc(HealthIncidentModel.timestamp))
        .limit(limit)
    )
    return res.scalars().all()

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(GasAlertModel).where(GasAlertModel.id == alert_id))
    alert = res.scalar_one_or_none()
    if alert:
        alert.resolved = True
        await db.commit()
        return {"status": "acknowledged", "id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/api/standards")
async def get_standards_registry():
    """Returns the regulatory and medical standards registry."""
    return {
        "atmosphericGases": [
            {
                "gas": "Oxygen (O₂)",
                "nominal": "20.9% vol",
                "warningLimit": "< 19.5% vol",
                "criticalLimit": "< 18.0% vol",
                "source": "OSHA 29 CFR 1910.134 & DGMS Circulars",
                "effect": "Hypoxia, dizziness, unconsciousness, fatal asphyxiation below 18%"
            },
            {
                "gas": "Methane (CH₄)",
                "nominal": "< 0.1% vol",
                "warningLimit": "≥ 1.0% vol (Action threshold)",
                "criticalLimit": "≥ 1.5% vol (Mandatory Evacuate)",
                "source": "30 CFR §75.323 & CMR 2017 Regulation 169",
                "effect": "Combustible gas, explosive range 5% - 15% in presence of air"
            },
            {
                "gas": "Carbon Monoxide (CO)",
                "nominal": "< 10 ppm",
                "warningLimit": "≥ 25 ppm",
                "criticalLimit": "≥ 50 ppm (8-hour PEL)",
                "source": "OSHA Table Z-1 & DGMS Mine Safety Standard",
                "effect": "Chemical asphyxiant, binds with hemoglobin to form carboxyhemoglobin"
            },
            {
                "gas": "Hydrogen Sulfide (H₂S)",
                "nominal": "0 ppm",
                "warningLimit": "≥ 5 ppm",
                "criticalLimit": "≥ 10 ppm (Ceiling limit)",
                "source": "ACGIH TLV & DGMS Occupational Standard",
                "effect": "Highly toxic, causes olfactory paralysis and rapid cellular asphyxiation"
            }
        ],
        "biometrics": [
            {
                "metric": "Resting Heart Rate",
                "nominal": "60 – 100 bpm",
                "warningLimit": "> 110 bpm",
                "criticalLimit": "> 138 bpm / < 48 bpm",
                "source": "MedlinePlus Medical Encyclopedia — Vital Signs",
                "effect": "Tachycardia, cardiac overload, syncope, heat exhaustion"
            },
            {
                "metric": "Blood Oxygen (SpO₂)",
                "nominal": "≥ 95%",
                "warningLimit": "91% – 94%",
                "criticalLimit": "< 90%",
                "source": "WHO Clinical Guidelines & Pulmonary Health",
                "effect": "Hypoxemia, cerebral oxygen deprivation"
            },
            {
                "metric": "Body Core Temp",
                "nominal": "36.5 – 37.3 °C",
                "warningLimit": "> 37.8 °C",
                "criticalLimit": "≥ 38.6 °C",
                "source": "NIOSH Occupational Heat Stress Criteria",
                "effect": "Hyperthermia, heat cramps, heat stroke collapse"
            },
            {
                "metric": "Respiratory Rate",
                "nominal": "12 – 20 brpm",
                "warningLimit": "> 24 brpm",
                "criticalLimit": "≥ 30 brpm / < 8 brpm",
                "source": "MedlinePlus Vital Signs Reference",
                "effect": "Hyperventilation, severe distress or toxic gas inhalation"
            }
        ]
    }

# ==================== FRONTEND STATIC SERVING ====================

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_index():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "MineGuard AI Safety Gateway Backend is running."}
