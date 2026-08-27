import json, unittest
from telemetry import TelemetryError, derive_safety_state, expected_signature, parse_and_validate, verify_signature
def sample_payload(): return {"sequence": 4, "timestamp": 1_700_000_000, "heartRateBpm": 76.0, "respiratoryRateBrpm": 15.0, "bodyTemperatureC": 36.8, "ambientOxygenPercent": 20.8, "methanePercent": 0.2, "carbonMonoxidePpm": 4.0}
class TelemetryTests(unittest.TestCase):
    def test_signature_and_normal_state(self):
        raw_body, secret = json.dumps(sample_payload(), separators=(",", ":")).encode(), b"demo-secret"; verify_signature(secret, raw_body, expected_signature(secret, raw_body)); self.assertEqual(derive_safety_state(parse_and_validate(raw_body, now=1_700_000_000)).level, "normal")
    def test_danger_state_for_low_oxygen_and_methane(self):
        payload = sample_payload(); payload.update({"ambientOxygenPercent": 19.2, "methanePercent": 1.6}); safety_state = derive_safety_state(payload); self.assertEqual(safety_state.level, "danger"); self.assertTrue(safety_state.local_alarm_required); self.assertIn("oxygen_deficient", safety_state.reasons)
    def test_rejects_stale_data(self):
        with self.assertRaises(TelemetryError): parse_and_validate(json.dumps(sample_payload()).encode(), now=1_700_000_121)
if __name__ == "__main__": unittest.main()
