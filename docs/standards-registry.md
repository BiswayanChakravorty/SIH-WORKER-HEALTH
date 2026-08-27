# Worker Health Band — Standard Registry

The product shows a **Standard** column beside every sensor value. The entries below are a transparent reference baseline for the prototype, not individualized clinical thresholds and not a substitute for the mine’s approved ventilation plan, gas-monitor specification, emergency procedure, sensor calibration policy, or legally required certified equipment.

## Applied reference values

| Metric | Standard shown in the app | Meaning in this prototype | Authoritative source |
|---|---|---|---|
| Resting heart rate | **60–100 bpm** | General adult resting reference band; an out-of-range flag is an attention cue, not a diagnosis. | [MedlinePlus vital signs][1] |
| Resting respiratory rate | **12–18 breaths/min** | General adult resting reference band; exercise, work conditions, health status, and personal baseline may differ. | [MedlinePlus vital signs][1] |
| Body temperature | **36.5–37.3 °C** | General adult resting reference band; measurement method and environment affect readings. | [MedlinePlus vital signs][1] |
| Ambient oxygen | **At least 19.5% O₂** | An atmosphere below 19.5% oxygen is shown as **Danger — oxygen deficient**. | [OSHA 29 CFR 1910.134 interpretation][2] |
| Methane | **1.0% warning; 1.5% evacuate/withdrawal condition** | The mobile prototype distinguishes a warning from a critical evacuation state for underground-coal-mine reference logic. | [30 CFR §75.323][3] |
| Carbon monoxide | **50 ppm, 8-hour PEL** | This is displayed as an occupational exposure limit, not a safe instantaneous alarm or a medical threshold. The approved site action level must be configured for the deployed system. | [OSHA Table Z-1][4] |

## Safety interpretation

MedlinePlus states that the vital-sign reference ranges above apply to an **average healthy adult while resting**. The mobile interface therefore labels them “general adult resting reference,” and it does not call a worker medically normal or medically unsafe from a wristband reading alone. The user should seek the site’s established clinical or emergency process if the system raises a vital-sign exception.[1]

For gas hazards, 30 CFR §75.323 requires action when methane reaches 1.0% or more in a working place or intake air course, and withdrawal from the affected area at 1.5% or more in the specified setting. The prototype uses these values to demonstrate a warning/critical sequence and highlights that local jurisdiction, mine type, work location, and an approved ventilation plan may impose different or stricter requirements.[3]

> **Operational boundary:** The C++ reference code makes a local alert immediately. The Python gateway and mobile app repeat and log the safety state; they do not replace certified monitoring, ventilation controls, emergency communications, or human direction.

## References

[1]: https://medlineplus.gov/ency/article/002341.htm "MedlinePlus Medical Encyclopedia — Vital signs"
[2]: https://www.osha.gov/laws-regs/standardinterpretations/2007-04-02-0 "OSHA — Clarification of breathing-air requirement of at least 19.5 percent oxygen"
[3]: https://www.ecfr.gov/current/title-30/chapter-I/subchapter-O/part-75/subpart-D/section-75.323 "eCFR — 30 CFR §75.323 Actions for excessive methane"
[4]: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1000TABLEZ1 "OSHA — 1910.1000 Table Z-1 Limits for Air Contaminants"
