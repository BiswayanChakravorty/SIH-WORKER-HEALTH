"""Configuration settings and mining safety thresholds (DGMS, OSHA, CMR 2017, 30 CFR §75.323)."""
import os

class Settings:
    # Server & Security
    APP_NAME: str = "MineGuard AI — Mine Worker IoT Safety Gateway"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    BAND_SHARED_SECRET: str = os.getenv("BAND_SHARED_SECRET", "sih-secret-mine-safety-key-2026")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./mine_safety.db")
    
    # Atmospheric Gas Thresholds (Mines Act / DGMS & 30 CFR §75.323)
    # Methane (CH4) %
    METHANE_WARNING_PCT: float = 1.0       # 1.0% Warning: inspect ventilation & cut unnecessary load
    METHANE_CRITICAL_PCT: float = 1.5      # 1.5% Critical: IMMEDIATE EVACUATION & electrical cutoff
    
    # Carbon Monoxide (CO) ppm
    CO_WARNING_PPM: float = 25.0           # 25 ppm Warning: Potential spontaneous combustion / smoldering
    CO_CRITICAL_PPM: float = 50.0          # 50 ppm Critical: OSHA 8-hr Permissible Exposure Limit (PEL)
    
    # Oxygen (O2) %
    O2_DEFICIENCY_PCT: float = 19.5        # < 19.5% Warning: Oxygen deficient atmosphere (OSHA / DGMS)
    O2_CRITICAL_PCT: float = 18.0          # < 18.0% Critical: Severe hypoxia risk, emergency oxygen required
    
    # Hydrogen Sulfide (H2S) ppm
    H2S_WARNING_PPM: float = 5.0           # 5 ppm Warning: Toxic gas accumulation
    H2S_CRITICAL_PPM: float = 10.0         # 10 ppm Critical: Highly toxic, immediate withdrawal
    
    # Vital Sign Health Thresholds (Mining Occupational Health Standards)
    # Heart Rate (BPM)
    HR_RESTING_MIN: float = 60.0
    HR_RESTING_MAX: float = 100.0
    HR_WARNING_MAX: float = 110.0          # Elevated physical strain
    HR_CRITICAL_MAX: float = 138.0         # Severe cardiovascular strain / Tachycardia
    HR_CRITICAL_MIN: float = 48.0          # Severe Bradycardia / syncopal risk
    
    # Respiratory Rate (Breaths per minute)
    RESP_MIN: float = 12.0
    RESP_MAX: float = 20.0
    RESP_WARNING_MAX: float = 24.0
    RESP_CRITICAL_MAX: float = 30.0        # Tachypnea (hyperventilation / gas inhalation)
    RESP_CRITICAL_MIN: float = 8.0         # Respiratory depression
    
    # Blood Oxygen SpO2 (%)
    SPO2_NORMAL_MIN: float = 95.0
    SPO2_WARNING_MIN: float = 92.0         # Mild Hypoxia
    SPO2_CRITICAL_MIN: float = 88.0        # Severe Hypoxia / Suffocation Risk
    
    # Body / Skin Temperature (°C)
    TEMP_NORMAL_MIN: float = 36.5
    TEMP_NORMAL_MAX: float = 37.3
    TEMP_WARNING_MAX: float = 37.8         # Moderate thermal stress
    TEMP_CRITICAL_MAX: float = 38.6        # Heat Stroke / Hyperthermia risk
    
    # Accelerometer / Impact
    FALL_ACCEL_THRESHOLD_G: float = 2.8    # G-force threshold for fall / rockfall impact
    
    # Telemetry Freshness
    MAX_MESSAGE_AGE_SECONDS: int = 120

settings = Settings()
