# Worker Health Band — Website Design Plan

The responsive website will be an operational safety dashboard rather than a mobile tab interface. It will keep the deep mine-navy and signal-teal identity, use a persistent safety navigation rail on desktop, and collapse to a compact header on mobile screens. The principal workspace will show the highest current risk, the band connection state, visualized vital readings, a **Reading / Standard / Status** table, and a source-aware standards panel.

| Website region | Content | Interaction |
|---|---|---|
| Safety header | Worker identity, active shift, band connection, and safety state. | Exposes the current hazard state without scrolling. |
| Monitor overview | Heart rate, breathing rate, body temperature, ambient oxygen, methane, and carbon monoxide cards. | Allows rapid scanning of telemetry. |
| Standard comparison | Reading, standard, status, authority, and source link per metric. | Makes every safety indication traceable to its source. |
| Alarm workflow | Demo gas-alarm control, active-hazard guidance, acknowledgement, and reset. | Demonstrates that acknowledgement does not resolve a hazard. |
| Architecture panel | C++ wristband, authenticated Python gateway, and browser dashboard flow. | Clarifies the language split and deployment boundary. |

The website will use deterministic demonstration telemetry and will clearly describe the safety and certification boundary. The existing C++ firmware and Python gateway reference modules remain part of the codebase as the integration specification.
