export type RiskLevel = "normal" | "caution" | "danger";

export type MetricKey =
  | "heartRateBpm"
  | "respiratoryRateBrpm"
  | "bodyTemperatureC"
  | "ambientOxygenPercent"
  | "methanePercent"
  | "carbonMonoxidePpm";

export interface BandTelemetry {
  workerId: string;
  workerName: string;
  bandId: string;
  recordedAt: string;
  heartRateBpm: number;
  respiratoryRateBrpm: number;
  bodyTemperatureC: number;
  ambientOxygenPercent: number;
  methanePercent: number;
  carbonMonoxidePpm: number;
}

export interface SafetyStandard {
  key: MetricKey;
  label: string;
  unit: string;
  standard: string;
  authority: string;
  sourceUrl: string;
  sourceShortName: string;
  scopeNote: string;
}

export interface MetricAssessment {
  key: MetricKey;
  label: string;
  value: number;
  valueLabel: string;
  standard: SafetyStandard;
  level: RiskLevel;
  statusLabel: string;
  detail: string;
}

export interface SafetyEvaluation {
  overallLevel: RiskLevel;
  overallLabel: string;
  assessments: MetricAssessment[];
  hasGasHazard: boolean;
}

export const SAFETY_STANDARDS: SafetyStandard[] = [
  { key: "heartRateBpm", label: "Heart rate", unit: "bpm", standard: "60–100 bpm", authority: "NIH / MedlinePlus", sourceShortName: "MedlinePlus vital signs", sourceUrl: "https://medlineplus.gov/ency/article/002341.htm", scopeNote: "General adult resting reference; not an individualized clinical threshold." },
  { key: "respiratoryRateBrpm", label: "Respiratory rate", unit: "breaths/min", standard: "12–18 breaths/min", authority: "NIH / MedlinePlus", sourceShortName: "MedlinePlus vital signs", sourceUrl: "https://medlineplus.gov/ency/article/002341.htm", scopeNote: "General adult resting reference; exertion and personal baseline can differ." },
  { key: "bodyTemperatureC", label: "Body temperature", unit: "°C", standard: "36.5–37.3 °C", authority: "NIH / MedlinePlus", sourceShortName: "MedlinePlus vital signs", sourceUrl: "https://medlineplus.gov/ency/article/002341.htm", scopeNote: "General adult resting reference; method and environment affect readings." },
  { key: "ambientOxygenPercent", label: "Ambient oxygen", unit: "% O₂", standard: "At least 19.5% O₂", authority: "U.S. OSHA", sourceShortName: "OSHA oxygen-deficiency interpretation", sourceUrl: "https://www.osha.gov/laws-regs/standardinterpretations/2007-04-02-0", scopeNote: "Below 19.5% is oxygen-deficient; a danger condition in this prototype." },
  { key: "methanePercent", label: "Methane", unit: "% CH₄", standard: "1.0% warning • 1.5% withdrawal", authority: "MSHA / 30 CFR §75.323", sourceShortName: "30 CFR §75.323", sourceUrl: "https://www.ecfr.gov/current/title-30/chapter-I/subchapter-O/part-75/subpart-D/section-75.323", scopeNote: "Underground-coal-mine reference. Local ventilation plans may be stricter." },
  { key: "carbonMonoxidePpm", label: "Carbon monoxide", unit: "ppm", standard: "50 ppm (8-hour PEL)", authority: "U.S. OSHA Table Z-1", sourceShortName: "OSHA Table Z-1", sourceUrl: "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1000TABLEZ1", scopeNote: "An 8-hour occupational exposure limit, not a safe instantaneous alarm threshold." },
];

export const NORMAL_DEMO_TELEMETRY: BandTelemetry = { workerId: "MW-0742", workerName: "Arjun Singh", bandId: "WHB-042", recordedAt: "Demo telemetry • current session", heartRateBpm: 76, respiratoryRateBrpm: 15, bodyTemperatureC: 36.8, ambientOxygenPercent: 20.8, methanePercent: 0.2, carbonMonoxidePpm: 4 };
export const GAS_ALARM_DEMO_TELEMETRY: BandTelemetry = { ...NORMAL_DEMO_TELEMETRY, recordedAt: "Demo gas alarm • current session", ambientOxygenPercent: 19.2, methanePercent: 1.6, carbonMonoxidePpm: 54 };

const standardByKey = Object.fromEntries(SAFETY_STANDARDS.map((standard) => [standard.key, standard])) as Record<MetricKey, SafetyStandard>;
const numberLabel = (value: number, key: MetricKey) => ["bodyTemperatureC", "ambientOxygenPercent", "methanePercent"].includes(key) ? value.toFixed(1) : String(Math.round(value));

function assessment(telemetry: BandTelemetry, key: MetricKey): MetricAssessment {
  const standard = standardByKey[key];
  const value = telemetry[key];
  const base = { key, label: standard.label, value, valueLabel: `${numberLabel(value, key)} ${standard.unit}`, standard };
  if (key === "heartRateBpm" || key === "respiratoryRateBrpm" || key === "bodyTemperatureC") {
    const bounds = key === "heartRateBpm" ? [60, 100] : key === "respiratoryRateBrpm" ? [12, 18] : [36.5, 37.3];
    return value < bounds[0] || value > bounds[1] ? { ...base, level: "caution", statusLabel: "Review", detail: "Outside the general adult resting reference." } : { ...base, level: "normal", statusLabel: "Within reference", detail: "Within the general adult resting reference." };
  }
  if (key === "ambientOxygenPercent") return value < 19.5 ? { ...base, level: "danger", statusLabel: "Oxygen deficient", detail: "Below the 19.5% oxygen reference; take site-directed emergency action." } : { ...base, level: "normal", statusLabel: "Normal", detail: "At or above the 19.5% oxygen reference." };
  if (key === "methanePercent") return value >= 1.5 ? { ...base, level: "danger", statusLabel: "Withdrawal condition", detail: "At or above the 1.5% methane withdrawal reference." } : value >= 1.0 ? { ...base, level: "caution", statusLabel: "Methane warning", detail: "At or above the 1.0% methane warning reference." } : { ...base, level: "normal", statusLabel: "Normal", detail: "Below the methane warning reference." };
  return value >= 50 ? { ...base, level: "caution", statusLabel: "Exposure limit reached", detail: "At or above the displayed 8-hour CO exposure limit." } : { ...base, level: "normal", statusLabel: "Normal", detail: "Below the displayed 8-hour CO exposure limit." };
}

export function evaluateTelemetry(telemetry: BandTelemetry): SafetyEvaluation {
  const assessments = SAFETY_STANDARDS.map((standard) => assessment(telemetry, standard.key));
  const hasDanger = assessments.some((item) => item.level === "danger");
  const hasCaution = assessments.some((item) => item.level === "caution");
  return { assessments, hasGasHazard: assessments.some((item) => ["ambientOxygenPercent", "methanePercent", "carbonMonoxidePpm"].includes(item.key) && item.level !== "normal"), overallLevel: hasDanger ? "danger" : hasCaution ? "caution" : "normal", overallLabel: hasDanger ? "Danger detected" : hasCaution ? "Needs review" : "All readings stable" };
}

export const riskColors: Record<RiskLevel, { background: string; border: string; text: string; label: string }> = { normal: { background: "#E9F9F5", border: "#99E2D6", text: "#087D70", label: "Normal" }, caution: { background: "#FFF5E3", border: "#F7CC82", text: "#B54708", label: "Caution" }, danger: { background: "#FEF0EE", border: "#F7B2AC", text: "#B42318", label: "Danger" } };
