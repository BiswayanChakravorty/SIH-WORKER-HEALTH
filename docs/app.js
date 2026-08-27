const normalReadings = [
  { group: "health", icon: "♥", name: "Heart rate", value: "76 bpm", standard: "60–100 bpm", source: "https://medlineplus.gov/ency/article/002341.htm", status: "Within reference" },
  { group: "health", icon: "≋", name: "Respiratory rate", value: "15 breaths/min", standard: "12–18 breaths/min", source: "https://medlineplus.gov/ency/article/002341.htm", status: "Within reference" },
  { group: "health", icon: "♨", name: "Body temperature", value: "36.8 °C", standard: "36.5–37.3 °C", source: "https://medlineplus.gov/ency/article/002341.htm", status: "Within reference" },
  { group: "gas", icon: "≋", name: "Ambient oxygen", value: "20.8 % O₂", standard: "At least 19.5% O₂", source: "https://www.osha.gov/laws-regs/standardinterpretations/2007-04-02-0", status: "Normal" },
  { group: "gas", icon: "♨", name: "Methane", value: "0.2 % CH₄", standard: "1.0% warning · 1.5% withdrawal", source: "https://www.ecfr.gov/current/title-30/chapter-I/subchapter-O/part-75/subpart-D/section-75.323", status: "Normal" },
  { group: "gas", icon: "☁", name: "Carbon monoxide", value: "4 ppm", standard: "50 ppm (8-hour PEL)", source: "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1000TABLEZ1", status: "Normal" },
];

const dangerValues = { "Ambient oxygen": "18.7 % O₂", Methane: "1.7 % CH₄", "Carbon monoxide": "61 ppm" };
let alarmActive = false;
let acknowledged = false;

function data() { return normalReadings.map(reading => ({ ...reading, value: alarmActive && dangerValues[reading.name] ? dangerValues[reading.name] : reading.value, danger: Boolean(alarmActive && dangerValues[reading.name]) })); }
function card(reading) { return `<article class="metric-card"><div class="metric-top"><span class="metric-icon">${reading.icon}</span><span class="pill ${reading.danger ? "danger" : ""}">${reading.danger ? "Danger" : "Normal"}</span></div><span class="metric-label">${reading.name}</span><strong class="metric-value">${reading.value}</strong><span class="metric-standard">Standard: ${reading.standard}</span></article>`; }
function rows(readings) { return readings.map(reading => `<div class="table-row" role="row"><span class="sensor">${reading.name}</span><span class="value">${reading.value}</span><a href="${reading.source}" target="_blank" rel="noreferrer">${reading.standard} ↗</a><span><b class="status-pill ${reading.danger ? "danger" : ""}">${reading.danger ? "Unsafe" : reading.status}</b></span></div>`).join(""); }
function render() {
  const readings = data();
  document.querySelector("#health-cards").innerHTML = readings.filter(x => x.group === "health").map(card).join("");
  document.querySelector("#gas-cards").innerHTML = readings.filter(x => x.group === "gas").map(card).join("");
  document.querySelector("#standard-rows").innerHTML = rows(readings);
  const banner = document.querySelector("#safety-banner"), summary = document.querySelector("#alarm-summary"), copy = document.querySelector("#alarm-copy"), title = document.querySelector("#safety-title"), message = document.querySelector("#safety-message"), tag = document.querySelector("#safety-tag"), symbol = document.querySelector("#safety-symbol"), active = document.querySelector("#active-gases"), run = document.querySelector("#alarm-button"), ack = document.querySelector("#ack-button"), reset = document.querySelector("#reset-button");
  banner.className = `safety-banner ${alarmActive ? "danger" : "safe"}`; summary.className = `alarm-summary ${alarmActive ? "danger" : "safe"}`;
  title.textContent = alarmActive ? "Unsafe gas condition detected" : "All readings stable"; message.textContent = alarmActive ? "Leave the area and follow your approved mine emergency procedure." : "Latest sensor values are below the displayed hazard thresholds."; tag.textContent = alarmActive ? "Demo alert" : "Live demo"; symbol.textContent = alarmActive ? "!" : "✓";
  summary.textContent = alarmActive ? (acknowledged ? "Alert acknowledged — hazard still active" : "Unsafe gas condition detected") : "No active gas hazard";
  copy.textContent = alarmActive ? "Acknowledgement records the alert but does not resolve the hazardous reading." : "Use the test button to demonstrate the unsafe-gas alert state.";
  active.hidden = !alarmActive; active.innerHTML = alarmActive ? readings.filter(x => x.danger).map(x => `<div class="active-gas"><span>${x.name}</span><b>${x.value}</b></div>`).join("") : "";
  run.hidden = alarmActive; ack.hidden = !alarmActive; reset.hidden = !alarmActive; ack.textContent = acknowledged ? "Acknowledged" : "Acknowledge"; ack.disabled = acknowledged;
}
document.querySelector("#alarm-button").addEventListener("click", () => { alarmActive = true; acknowledged = false; render(); });
document.querySelector("#ack-button").addEventListener("click", () => { acknowledged = true; render(); });
document.querySelector("#reset-button").addEventListener("click", () => { alarmActive = false; acknowledged = false; render(); });
render();

