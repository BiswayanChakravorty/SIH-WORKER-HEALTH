# Worker Health Band — Mobile Interface Design

## Product intent

Worker Health Band is a **portrait-first companion for a mine-worker IoT wristband**. The interface is intended for a worker, shift supervisor, or safety officer to recognize a health or gas hazard in seconds. The working prototype will use explicitly labeled simulated wristband telemetry until a validated device connection is supplied; it is not a clinical diagnostic system or a substitute for site-specific emergency procedures.

## Screen list and primary content

| Screen | Primary content | Core functions |
|---|---|---|
| **Safety Home** | Connected-band state, current risk banner, last transmission time, worker and shift identity, and a concise status summary. | Recognize the highest-priority risk; open an active alert; acknowledge test-state alerts. |
| **Live Readings** | Heart rate, respiratory rate, body temperature, oxygen percentage, and detected gas readings. Each row includes **Reading**, **Standard**, and **Status** columns. | Compare live values with a cited reference band or exposure limit; see whether the value is within the configured warning state. |
| **Gas Safety** | Carbon monoxide, methane/LEL, oxygen-deficiency state, and a clear alarm condition. | Trigger a visible and haptic demo alarm when a hazardous level is detected; review guidance to evacuate and notify site control. |
| **Alert Detail** | Alert severity, timestamp, affected metric, current reading, applied threshold, source, and actions. | Acknowledge the alert locally, return to readings, and view the relevant standard/source note. |
| **Standards & Sources** | A transparent table of physiological reference ranges and occupational gas limits, including the authority, basis, and source link. | Make the “standard” column traceable; distinguish general adult reference ranges from site-specific occupational requirements. |
| **Band & Settings** | Band connection label, sensor availability, alarm-test control, accessibility preferences, and disclaimer. | Run a controlled alarm demonstration and show the boundary between the prototype and a certified emergency system. |

## Key user flows

The primary monitoring flow begins on **Safety Home**, where the user can see the band connection, worker identity, and a single clear overall state. Tapping “View live readings” opens the **Live Readings** screen. Each metric is placed in a three-column comparison: current telemetry, the applied standard, and the resulting state. Tapping any row opens the source-aware **Alert Detail** view if it is out of range.

The critical hazard flow is designed for one-handed operation. When the gas sensor detects a configured hazardous state, the application presents a full-width red alert card, activates haptic feedback where supported, and exposes a single primary action to view the response details. The **Alert Detail** screen states the required operational next step—such as leaving the area and notifying site control—without representing acknowledgment as a resolution. A local “Acknowledge” action records that the notification was seen in the prototype, while the alert remains visible until readings recover or the demo state is reset.

The safety-review flow opens **Standards & Sources** from the Live Readings header. This screen makes the meaning of the “Standard” column legible: physiological values are general adult reference ranges, while gas thresholds are authoritative exposure or mine-atmosphere limits that require replacement with the mine’s approved site procedure where it is stricter.

## Layout and interaction choices

The app is designed for a **9:16 portrait display** with the highest-risk information in the upper reach zone. The top portion contains connection and risk state; the primary next action is a full-width button in the lower-middle portion; tab targets use iOS-standard proportions with generous hit areas. Numbers use high-contrast tabular presentation and descriptions do not rely on color alone. Severe conditions use an icon, plain-language label, color, and priority order simultaneously.

| Element | Layout decision | Reason |
|---|---|---|
| **Risk banner** | Full-width card immediately under the header, at least two text cues plus an icon. | Critical information should be recognized without scrolling. |
| **Metric cards** | Two-column vital cards on Home; three-column table rows on Live Readings. | Home enables scanning; the detailed view satisfies the requested standard-column comparison. |
| **Primary alert action** | A single 48 px minimum-height red action, positioned before secondary actions. | Supports rapid, one-handed access in a stressful moment. |
| **Bottom navigation** | Home, Readings, Alerts, Standards. | Keeps the core safety loop immediately reachable. |

## Color choices

The visual identity uses **deep mine navy `#0B1F33`** for dependable structure, **signal teal `#12B6A6`** for a connected and normal state, **amber `#F59E0B`** for a cautionary state, and **emergency red `#D92D20`** for gas or physiological alarms. The canvas is a cool off-white `#F7F9FC` with white elevated cards. Navy text on white provides a clear default contrast, while colors are paired with words and icons for accessibility.

## Data model and integration boundary

| Model | Key fields | Prototype source |
|---|---|---|
| `BandTelemetry` | `heartRateBpm`, `respiratoryRateBrpm`, `bodyTemperatureC`, `spo2Percent`, `coPpm`, `methaneLELPercent`, `oxygenPercent`, `recordedAt` | Local deterministic fixture, clearly marked “Demo band”. |
| `SafetyStandard` | `metric`, `displayRange`, `warningRule`, `authority`, `sourceUrl`, `scopeNote` | Versioned in-app standard registry validated during research. |
| `SafetyAlert` | `id`, `severity`, `metric`, `value`, `threshold`, `createdAt`, `acknowledgedAt` | Derived from telemetry against the standard registry. |

Hardware data must arrive through a secure, authenticated device or gateway integration defined by the mine operator. Until that protocol and backend are available, the app will not imply real Bluetooth, emergency dispatch, or medical-device certification.
