"""Database configuration, SQLAlchemy models, and initial seed repository."""
from __future__ import annotations
import time
from typing import AsyncGenerator
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, create_engine, select, desc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./mine_safety.db"
SYNC_DATABASE_URL = "sqlite:///./mine_safety.db"

Base = declarative_base()

class WorkerModel(Base):
    __tablename__ = "workers"
    id = Column(String(32), primary_key=True)
    name = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)
    blood_group = Column(String(8), default="O+")
    emergency_contact = Column(String(32), default="+91-9876543210")
    assigned_band_id = Column(String(32), nullable=False)
    current_zone = Column(String(128), default="North Drift 04 (L-220m)")
    status = Column(String(32), default="NORMAL")  # NORMAL, CAUTION, DANGER, EVACUATED
    battery_pct = Column(Integer, default=95)
    last_seen = Column(Integer, default=lambda: int(time.time()))

class TelemetryModel(Base):
    __tablename__ = "telemetry_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(String(32), index=True)
    band_id = Column(String(32))
    sequence = Column(Integer)
    timestamp = Column(Integer, index=True)
    heart_rate = Column(Float)
    respiratory_rate = Column(Float)
    body_temp = Column(Float)
    spo2 = Column(Float)
    ambient_o2 = Column(Float)
    methane_pct = Column(Float)
    co_ppm = Column(Float)
    h2s_ppm = Column(Float)
    fall_detected = Column(Boolean, default=False)
    battery_pct = Column(Integer, default=100)
    signal_strength = Column(Integer, default=-60)
    sos_triggered = Column(Boolean, default=False)
    mine_zone = Column(String(128))

class GasAlertModel(Base):
    __tablename__ = "gas_alerts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Integer, default=lambda: int(time.time()), index=True)
    worker_id = Column(String(32), index=True)
    zone = Column(String(128))
    gas_type = Column(String(32))  # CH4, CO, O2, H2S
    level = Column(String(32))     # WARNING, CRITICAL
    reading_value = Column(Float)
    threshold_value = Column(Float)
    resolved = Column(Boolean, default=False)
    action_taken = Column(Text, default="Automated safety siren broadcasted.")

class HealthIncidentModel(Base):
    __tablename__ = "health_incidents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Integer, default=lambda: int(time.time()), index=True)
    worker_id = Column(String(32), index=True)
    anomaly_type = Column(String(64))  # TACHYCARDIA, HYPOXIA, HEAT_EXHAUSTION, FALL
    severity = Column(String(32))      # CAUTION, DANGER
    heart_rate = Column(Float)
    spo2 = Column(Float)
    body_temp = Column(Float)
    resolved = Column(Boolean, default=False)
    notes = Column(Text, default="")

class ZoneModel(Base):
    __tablename__ = "mine_zones"
    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    depth_meters = Column(Integer, default=200)
    ventilation_status = Column(String(32), default="ACTIVE_OPTIMAL")  # ACTIVE_OPTIMAL, DEGRADED, CRITICAL_PURGE
    hazard_level = Column(String(32), default="SAFE")                 # SAFE, CAUTION, EVACUATE

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed default workers & zones if empty
    async with async_session_maker() as session:
        result = await session.execute(select(WorkerModel))
        workers = result.scalars().all()
        if not workers:
            default_workers = [
                WorkerModel(
                    id="MW-0742",
                    name="Arjun Singh",
                    role="Drill Operator & Face Miner",
                    blood_group="B+",
                    emergency_contact="+91-9845012345",
                    assigned_band_id="WHB-042",
                    current_zone="North Drift 04 (L-220m)",
                    status="NORMAL",
                    battery_pct=92,
                    last_seen=int(time.time())
                ),
                WorkerModel(
                    id="MW-0743",
                    name="Rajesh Kumar",
                    role="Ventilation Inspector",
                    blood_group="O+",
                    emergency_contact="+91-9876509876",
                    assigned_band_id="WHB-043",
                    current_zone="East Return Air Course (L-180m)",
                    status="NORMAL",
                    battery_pct=88,
                    last_seen=int(time.time())
                ),
                WorkerModel(
                    id="MW-0744",
                    name="Sunita Soren",
                    role="Underground Electrician & Blasting Tech",
                    blood_group="A+",
                    emergency_contact="+91-9823456789",
                    assigned_band_id="WHB-044",
                    current_zone="South Stope 02 (L-350m)",
                    status="NORMAL",
                    battery_pct=96,
                    last_seen=int(time.time())
                ),
                WorkerModel(
                    id="MW-0745",
                    name="Mohammed Irfan",
                    role="Haulage & Conveyor Specialist",
                    blood_group="AB+",
                    emergency_contact="+91-9811223344",
                    assigned_band_id="WHB-045",
                    current_zone="Main Incline Conveyor (L-120m)",
                    status="NORMAL",
                    battery_pct=79,
                    last_seen=int(time.time())
                )
            ]
            session.add_all(default_workers)

            default_zones = [
                ZoneModel(id="Z-01", name="North Drift 04 (L-220m)", depth_meters=220, ventilation_status="ACTIVE_OPTIMAL", hazard_level="SAFE"),
                ZoneModel(id="Z-02", name="East Return Air Course (L-180m)", depth_meters=180, ventilation_status="ACTIVE_OPTIMAL", hazard_level="SAFE"),
                ZoneModel(id="Z-03", name="South Stope 02 (L-350m)", depth_meters=350, ventilation_status="ACTIVE_OPTIMAL", hazard_level="SAFE"),
                ZoneModel(id="Z-04", name="Main Incline Conveyor (L-120m)", depth_meters=120, ventilation_status="ACTIVE_OPTIMAL", hazard_level="SAFE"),
                ZoneModel(id="Z-05", name="Shaft 01 Intake (L-0m Surface)", depth_meters=0, ventilation_status="ACTIVE_OPTIMAL", hazard_level="SAFE")
            ]
            session.add_all(default_zones)
            await session.commit()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
