# Website Conversion Handoff

The selected GitHub repository was empty at inspection. The prior mobile prototype established the product requirements and the reusable source material for the website conversion.

| Artifact | Reuse in website |
|---|---|
| `docs/standards-registry.md` | Standard column copy, source URLs, scope and safety limitations. |
| `reference_impl/firmware/worker_health_band.cpp` | C++ wristband firmware reference and telemetry field names. |
| `reference_impl/gateway/telemetry.py` | Python gateway validation and safety-state logic. |
| `lib/safety.ts` | Demonstration thresholds and normal / caution / danger state model. |
| Generated Worker Health Band icon | Visual identity for the responsive dashboard. |

The web dashboard must show the same fields and preserve the local-first alarm principle: local device alarm first; server and browser status mirror it.
