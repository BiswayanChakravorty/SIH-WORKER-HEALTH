"""Reference Python telemetry validation and safety-state derivation."""
from __future__ import annotations
import hmac, json, time
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping
METHANE_WARNING_PERCENT, METHANE_WITHDRAWAL_PERCENT, MINIMUM_OXYGEN_PERCENT, CARBON_MONOXIDE_PEL_PPM, MAX_MESSAGE_AGE_SECONDS = 1.0, 1.5, 19.5, 50.0, 120
class TelemetryError(ValueError): pass
@dataclass(frozen=True)
class GatewaySafetyState: level: str; local_alarm_required: bool; reasons: tuple[str, ...]
REQUIRED_NUMERIC_FIELDS = ("sequence", "timestamp", "heartRateBpm", "respiratoryRateBrpm", "bodyTemperatureC", "ambientOxygenPercent", "methanePercent", "carbonMonoxidePpm")
def expected_signature(shared_secret: bytes, raw_body: bytes) -> str: return hmac.new(shared_secret, raw_body, sha256).hexdigest()
def verify_signature(shared_secret: bytes, raw_body: bytes, supplied_signature: str | None) -> None:
    if not supplied_signature: raise TelemetryError("missing X-Band-Signature")
    if not hmac.compare_digest(expected_signature(shared_secret, raw_body), supplied_signature): raise TelemetryError("invalid X-Band-Signature")
def parse_and_validate(raw_body: bytes, now: int | None = None) -> dict[str, float | int | str | bool]:
    try: payload: dict[str, Any] = json.loads(raw_body)
    except json.JSONDecodeError as error: raise TelemetryError("invalid JSON") from error
    if not isinstance(payload, dict): raise TelemetryError("telemetry must be a JSON object")
    for field in REQUIRED_NUMERIC_FIELDS:
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)): raise TelemetryError(f"{field} must be numeric")
    observed_at, reference_time = int(payload["timestamp"]), int(time.time()) if now is None else now
    if abs(reference_time - observed_at) > MAX_MESSAGE_AGE_SECONDS: raise TelemetryError("stale or future telemetry")
    if not 0.0 <= float(payload["ambientOxygenPercent"]) <= 100.0: raise TelemetryError("ambientOxygenPercent is outside physical bounds")
    if not 0.0 <= float(payload["methanePercent"]) <= 100.0: raise TelemetryError("methanePercent is outside physical bounds")
    if float(payload["carbonMonoxidePpm"]) < 0.0: raise TelemetryError("carbonMonoxidePpm cannot be negative")
    return payload
def derive_safety_state(payload: Mapping[str, float | int | str | bool]) -> GatewaySafetyState:
    reasons: list[str] = []; methane, oxygen, carbon_monoxide = float(payload["methanePercent"]), float(payload["ambientOxygenPercent"]), float(payload["carbonMonoxidePpm"])
    if oxygen < MINIMUM_OXYGEN_PERCENT: reasons.append("oxygen_deficient")
    if methane >= METHANE_WITHDRAWAL_PERCENT: reasons.append("methane_withdrawal_condition")
    if methane >= METHANE_WARNING_PERCENT: reasons.append("methane_warning")
    if carbon_monoxide >= CARBON_MONOXIDE_PEL_PPM: reasons.append("co_exposure_limit_reached")
    danger = "oxygen_deficient" in reasons or "methane_withdrawal_condition" in reasons
    return GatewaySafetyState(level="danger" if danger else "caution" if reasons else "normal", local_alarm_required=bool(reasons), reasons=tuple(reasons))
def mobile_status_payload(payload: Mapping[str, float | int | str | bool]) -> dict[str, Any]:
    safety_state = derive_safety_state(payload); return {"telemetry": dict(payload), "safetyState": {"level": safety_state.level, "localAlarmRequired": safety_state.local_alarm_required, "reasons": safety_state.reasons}, "gatewayProcessedAt": int(time.time())}
