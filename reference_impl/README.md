# Hardware and Gateway Reference Modules

This directory contains **reference integration code** that makes the language split explicit: C++ is for wristband firmware logic, Python is for the authenticated gateway, and the Expo mobile project renders the worker-facing experience. These modules are deliberately not executed inside the managed mobile application.

| Layer | Language | Responsibility |
|---|---|---|
| Wristband | C++17 | Acquire calibrated measurements, calculate local alarm state first, actuate alarm, and transmit signed telemetry. |
| Gateway | Python | Verify HMAC signature, reject stale or malformed data, derive a mirrored safety state, and expose a mobile-ready JSON payload. |
| Mobile companion | TypeScript | Show the status, Reading / Standard / Status comparison, alert flow, and source traceability. |

The C++ firmware sends JSON with `sequence`, `timestamp`, `heartRateBpm`, `respiratoryRateBrpm`, `bodyTemperatureC`, `ambientOxygenPercent`, `methanePercent`, and `carbonMonoxidePpm`. Sign the exact UTF-8 request body using HMAC-SHA256 and send the hexadecimal signature in `X-Band-Signature`. The gateway rejects unsigned, invalid, stale, future-dated, or physically implausible telemetry.

Use a protected device key store, transport security, anti-replay strategy, hardware-specific calibration procedure, and intrinsically safe approved equipment suitable for the selected mine. The standards rationale is documented in [`../docs/standards-registry.md`](../docs/standards-registry.md).
