// Reference C++17 firmware logic. Validate all hardware drivers, calibration and approvals separately.
#include <array>
#include <cstdio>
#include <string>
namespace worker_health_band {
enum class RiskLevel { Normal, Caution, Danger };
struct SensorFrame { unsigned long sequence; unsigned long unix_time; float heart_rate_bpm; float respiratory_rate_brpm; float body_temperature_c; float ambient_oxygen_percent; float methane_percent; float carbon_monoxide_ppm; };
struct SafetyState { RiskLevel overall; bool local_alarm_required; bool methane_warning; bool methane_withdrawal; bool oxygen_deficient; bool carbon_monoxide_limit_reached; };
constexpr float kMethaneWarningPercent = 1.0F; constexpr float kMethaneWithdrawalPercent = 1.5F; constexpr float kMinimumOxygenPercent = 19.5F; constexpr float kCarbonMonoxidePelPpm = 50.0F;
SafetyState evaluate_safety(const SensorFrame& frame) { const bool methane_withdrawal = frame.methane_percent >= kMethaneWithdrawalPercent; const bool methane_warning = frame.methane_percent >= kMethaneWarningPercent; const bool oxygen_deficient = frame.ambient_oxygen_percent < kMinimumOxygenPercent; const bool co_limit_reached = frame.carbon_monoxide_ppm >= kCarbonMonoxidePelPpm; const RiskLevel overall = (methane_withdrawal || oxygen_deficient) ? RiskLevel::Danger : (methane_warning || co_limit_reached) ? RiskLevel::Caution : RiskLevel::Normal; return {overall, overall != RiskLevel::Normal, methane_warning, methane_withdrawal, oxygen_deficient, co_limit_reached}; }
class SensorBoard { public: virtual ~SensorBoard() = default; virtual SensorFrame read_calibrated_frame() = 0; };
class LocalAlarm { public: virtual ~LocalAlarm() = default; virtual void set_alarm(bool enabled, RiskLevel severity) = 0; };
class AuthenticatedUplink { public: virtual ~AuthenticatedUplink() = default; virtual bool send_signed_payload(const std::string& canonical_json) = 0; };
std::string serialise_telemetry(const SensorFrame& frame, const SafetyState& state) { const char* level = state.overall == RiskLevel::Danger ? "danger" : state.overall == RiskLevel::Caution ? "caution" : "normal"; std::array<char, 512> json{}; std::snprintf(json.data(), json.size(), "{\"sequence\":%lu,\"timestamp\":%lu,\"heartRateBpm\":%.1f,\"respiratoryRateBrpm\":%.1f,\"bodyTemperatureC\":%.1f,\"ambientOxygenPercent\":%.1f,\"methanePercent\":%.2f,\"carbonMonoxidePpm\":%.1f,\"safetyState\":\"%s\",\"localAlarm\":%s}", frame.sequence, frame.unix_time, frame.heart_rate_bpm, frame.respiratory_rate_brpm, frame.body_temperature_c, frame.ambient_oxygen_percent, frame.methane_percent, frame.carbon_monoxide_ppm, level, state.local_alarm_required ? "true" : "false"); return json.data(); }
void monitor_once(SensorBoard& sensors, LocalAlarm& alarm, AuthenticatedUplink& uplink) { const SensorFrame frame = sensors.read_calibrated_frame(); const SafetyState state = evaluate_safety(frame); alarm.set_alarm(state.local_alarm_required, state.overall); (void)uplink.send_signed_payload(serialise_telemetry(frame, state)); }
}  // namespace worker_health_band
