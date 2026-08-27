"""Reference FastAPI entry point; deploy separately from the managed mobile application."""
from __future__ import annotations
import os
from fastapi import FastAPI, Header, HTTPException, Request
from telemetry import TelemetryError, mobile_status_payload, parse_and_validate, verify_signature
app = FastAPI(title="Worker Health Band Gateway", version="0.1.0")
def get_shared_secret() -> bytes:
    secret = os.environ.get("BAND_SHARED_SECRET")
    if not secret: raise RuntimeError("BAND_SHARED_SECRET must be configured by the gateway operator")
    return secret.encode("utf-8")
@app.post("/v1/telemetry")
async def ingest_telemetry(request: Request, x_band_signature: str | None = Header(default=None)):
    raw_body = await request.body()
    try:
        verify_signature(get_shared_secret(), raw_body, x_band_signature); return mobile_status_payload(parse_and_validate(raw_body))
    except (TelemetryError, RuntimeError) as error:
        raise HTTPException(status_code=401 if "Signature" in str(error) else 422, detail=str(error)) from error
