/**
 * MineGuard AI — Clean, Focused Frontend Controller
 */

let socket = null;
let audioContext = null;
let isAudioEnabled = true;
let isSirenPlaying = false;
let chartInstance = null;

// Initialize Web Audio API for Alarm
function initAudio() {
  if (!audioContext) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (AudioCtx) audioContext = new AudioCtx();
  }
}

function playAlarmSound(isCritical = true) {
  if (!isAudioEnabled) return;
  initAudio();
  if (!audioContext || isSirenPlaying) return;

  try {
    if (audioContext.state === 'suspended') audioContext.resume();

    const osc = audioContext.createOscillator();
    const gain = audioContext.createGain();
    const now = audioContext.currentTime;

    if (isCritical) {
      // 880Hz -> 440Hz sweep siren
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.4);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.8);
      gain.gain.setValueAtTime(0.18, now);
    } else {
      // Caution beep
      osc.type = 'sine';
      osc.frequency.setValueAtTime(600, now);
      gain.gain.setValueAtTime(0.1, now);
    }

    osc.connect(gain);
    gain.connect(audioContext.destination);

    osc.start();
    osc.stop(now + 0.8);
    isSirenPlaying = true;
    setTimeout(() => { isSirenPlaying = false; }, 900);
  } catch (err) {
    console.warn("Audio alarm blocked:", err);
  }
}

// Chart.js Setup
function initChart() {
  const ctx = document.getElementById('forecastChart');
  if (!ctx) return;

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Current', '+15 mins', '+30 mins', '+60 mins'],
      datasets: [
        {
          label: 'Heart Rate (BPM)',
          data: [74, 76, 78, 80],
          borderColor: '#f43f5e',
          backgroundColor: 'rgba(244, 63, 94, 0.1)',
          borderWidth: 3,
          tension: 0.3,
          pointRadius: 5,
          pointBackgroundColor: '#f43f5e',
          yAxisID: 'y'
        },
        {
          label: 'Fatigue Score (%)',
          data: [18.5, 24.0, 32.5, 45.0],
          borderColor: '#a855f7',
          backgroundColor: 'rgba(168, 85, 247, 0.15)',
          borderWidth: 3,
          borderDash: [5, 5],
          tension: 0.3,
          pointRadius: 5,
          pointBackgroundColor: '#a855f7',
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          labels: { color: '#cbd5e1', font: { family: 'Inter', size: 12, weight: 'bold' } }
        }
      },
      scales: {
        x: {
          grid: { color: '#1e293b' },
          ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
        },
        y: {
          type: 'linear',
          position: 'left',
          min: 40,
          max: 180,
          grid: { color: '#1e293b' },
          ticks: { color: '#f43f5e', font: { family: 'JetBrains Mono', size: 11 } },
          title: { display: true, text: 'Heart Rate (BPM)', color: '#f43f5e' }
        },
        y1: {
          type: 'linear',
          position: 'right',
          min: 0,
          max: 100,
          grid: { drawOnChartArea: false },
          ticks: { color: '#c084fc', font: { family: 'JetBrains Mono', size: 11 } },
          title: { display: true, text: 'Fatigue Score (%)', color: '#c084fc' }
        }
      }
    }
  });
}

// WebSocket Connection
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host || '127.0.0.1:8000';
  socket = new WebSocket(`${protocol}//${host}/ws/live`);

  socket.onopen = () => {
    console.log("[MineGuard] WebSocket Connected");
  };

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.data) updateUI(msg.data);
    } catch (e) {
      console.error("Parse error:", e);
    }
  };

  socket.onclose = () => {
    setTimeout(initWebSocket, 2000);
  };
}

// Update UI with Received Telemetry
function updateUI(data) {
  const tel = data.telemetry || {};
  const gas = data.gasSafety || {};
  const health = data.healthSafety || {};
  const forecast = data.healthForecast || {};
  const systemLevel = data.systemLevel || "SAFE";

  // 1. MASTER GAS BANNER & STATUS
  const banner = document.getElementById('gas-banner');
  const bannerIcon = document.getElementById('gas-banner-icon');
  const bannerTitle = document.getElementById('gas-banner-title');
  const bannerDesc = document.getElementById('gas-banner-desc');
  const sopBox = document.getElementById('gas-sop-alert');
  const sopText = document.getElementById('gas-sop-text');

  if (gas.overallLevel === "critical" || systemLevel === "CRITICAL") {
    banner.className = 'alert-banner banner-danger';
    bannerIcon.innerText = '🚨';
    bannerTitle.innerText = gas.hazardSummary || 'CRITICAL GAS HAZARD — EVACUATE!';
    bannerDesc.innerText = 'Gas readings exceed legal mining survival limits. Sound mine evacuation siren!';
    if (sopBox && gas.recommendedSOP) {
      sopBox.style.display = 'block';
      sopText.innerText = gas.recommendedSOP;
    }
    playAlarmSound(true);
  } else if (gas.overallLevel === "warning" || systemLevel === "WARNING") {
    banner.className = 'alert-banner banner-warning';
    bannerIcon.innerText = '⚠️';
    bannerTitle.innerText = gas.hazardSummary || 'ATMOSPHERIC GAS WARNING';
    bannerDesc.innerText = 'Gas concentrations elevated above baseline. Ventilation inspection required.';
    if (sopBox && gas.recommendedSOP) {
      sopBox.style.display = 'block';
      sopText.innerText = gas.recommendedSOP;
    }
    playAlarmSound(false);
  } else {
    banner.className = 'alert-banner banner-safe';
    bannerIcon.innerText = '✅';
    bannerTitle.innerText = 'ATMOSPHERE SAFE — NO HARMFUL GAS DETECTED';
    bannerDesc.innerText = 'All atmospheric sensor values are within legal DGMS & OSHA safety standards.';
    if (sopBox) sopBox.style.display = 'none';
  }

  // 2. GAS METERS (CH4, CO, O2, H2S)
  const ch4Val = parseFloat(tel.methanePercent ?? 0.08);
  const coVal = parseFloat(tel.carbonMonoxidePpm ?? 4.5);
  const o2Val = parseFloat(tel.ambientOxygenPercent ?? 20.9);
  const h2sVal = parseFloat(tel.hydrogenSulfidePpm ?? 0.0);

  updateGasCard('ch4', ch4Val, 1.0, 1.5, 3.0, (v) => v.toFixed(2));
  updateGasCard('co', coVal, 25.0, 50.0, 50.0, (v) => v.toFixed(1));
  updateOxygenCard('o2', o2Val);
  updateGasCard('h2s', h2sVal, 5.0, 10.0, 10.0, (v) => v.toFixed(1));

  // 3. VITALS (HR, Resp, SpO2, Temp)
  const hrVal = parseFloat(tel.heartRateBpm ?? 74);
  const respVal = parseFloat(tel.respiratoryRateBrpm ?? 15);
  const spo2Val = parseFloat(tel.spo2Percent ?? 98.2);
  const tempVal = parseFloat(tel.bodyTemperatureC ?? 36.8);

  updateVitalCard('hr', hrVal, hrVal >= 138 ? 'danger' : hrVal > 110 ? 'caution' : 'normal', hrVal >= 138 ? 'CRITICAL' : hrVal > 110 ? 'ELEVATED' : 'NORMAL');
  updateVitalCard('resp', respVal, respVal >= 30 || respVal <= 8 ? 'danger' : respVal > 24 ? 'caution' : 'normal', respVal >= 30 ? 'CRITICAL' : respVal > 24 ? 'ELEVATED' : 'NORMAL');
  updateVitalCard('spo2', spo2Val, spo2Val <= 88 ? 'danger' : spo2Val < 93 ? 'caution' : 'normal', spo2Val <= 88 ? 'HYPOXIA' : spo2Val < 93 ? 'MILD' : 'OPTIMAL');
  updateVitalCard('temp', tempVal, tempVal >= 38.6 ? 'danger' : tempVal > 37.8 ? 'caution' : 'normal', tempVal >= 38.6 ? 'HEAT STROKE' : tempVal > 37.8 ? 'ELEVATED' : 'NORMAL');

  // 4. FORECAST & PREDICTIONS
  const fatigueScore = parseFloat(forecast.fatigueScorePct ?? 18.5);
  const safeMins = forecast.estimatedSafeMinutesRemaining ?? 180;
  const riskLevel = forecast.fatigueRiskLevel || 'LOW';

  const valFatigue = document.getElementById('val-fatigue');
  const barFatigue = document.getElementById('bar-fatigue');
  const tagFatigue = document.getElementById('tag-fatigue');
  const valSafetime = document.getElementById('val-safetime');
  const txtAdvisory = document.getElementById('txt-advisory');

  if (valFatigue) valFatigue.innerText = fatigueScore.toFixed(1);
  if (barFatigue) barFatigue.style.width = `${Math.min(100, fatigueScore)}%`;
  if (valSafetime) valSafetime.innerText = `${safeMins} mins`;
  if (txtAdvisory && forecast.restRecommendation) txtAdvisory.innerText = forecast.restRecommendation;

  if (tagFatigue) {
    tagFatigue.innerText = `${riskLevel} RISK`;
    tagFatigue.className = `fatigue-tag ${riskLevel.toLowerCase()}`;
  }

  // Update Dynamic Forecast Chart
  if (chartInstance && forecast.timeline) {
    const hrPoints = [hrVal];
    const fatiguePoints = [fatigueScore];
    forecast.timeline.forEach(pt => {
      hrPoints.push(pt.predictedHeartRate);
      fatiguePoints.push(pt.predictedFatigueScore);
    });
    chartInstance.data.datasets[0].data = hrPoints;
    chartInstance.data.datasets[1].data = fatiguePoints;
    chartInstance.update('none');
  }
}

function updateGasCard(id, val, warnLimit, critLimit, maxScale, formatFn) {
  const card = document.getElementById(`card-${id}`);
  const valEl = document.getElementById(`val-${id}`);
  const tagEl = document.getElementById(`tag-${id}`);
  const barEl = document.getElementById(`bar-${id}`);

  if (valEl) valEl.innerText = formatFn(val);
  if (barEl) barEl.style.width = `${Math.min(100, (val / maxScale) * 100)}%`;

  let state = 'safe';
  let tagText = 'SAFE';
  if (val >= critLimit) {
    state = 'danger';
    tagText = 'CRITICAL';
  } else if (val >= warnLimit) {
    state = 'warning';
    tagText = 'WARNING';
  }

  if (card) card.className = `sensor-box ${state}`;
  if (tagEl) {
    tagEl.className = `status-tag tag-${state}`;
    tagEl.innerText = tagText;
  }
}

function updateOxygenCard(id, val) {
  const card = document.getElementById(`card-${id}`);
  const valEl = document.getElementById(`val-${id}`);
  const tagEl = document.getElementById(`tag-${id}`);
  const barEl = document.getElementById(`bar-${id}`);

  if (valEl) valEl.innerText = val.toFixed(1);
  if (barEl) barEl.style.width = `${Math.min(100, (val / 20.9) * 100)}%`;

  let state = 'safe';
  let tagText = 'OPTIMAL';
  if (val < 18.0) {
    state = 'danger';
    tagText = 'CRITICAL';
  } else if (val < 19.5) {
    state = 'warning';
    tagText = 'LOW';
  }

  if (card) card.className = `sensor-box ${state}`;
  if (tagEl) {
    tagEl.className = `status-tag tag-${state}`;
    tagEl.innerText = tagText;
  }
}

function updateVitalCard(id, val, stateClass, tagText) {
  const card = document.getElementById(`card-${id}`);
  const valEl = document.getElementById(`val-${id}`);
  const tagEl = document.getElementById(`tag-${id}`);

  if (valEl) valEl.innerText = id === 'temp' || id === 'spo2' ? val.toFixed(1) : val.toFixed(0);
  if (card) card.className = `vital-box ${stateClass}`;
  if (tagEl) {
    tagEl.className = `status-tag tag-${stateClass === 'caution' ? 'warning' : stateClass === 'danger' ? 'danger' : 'safe'}`;
    tagEl.innerText = tagText;
  }
}

// 1-Click Scenario Trigger
async function runScenario(scenario) {
  initAudio();
  const buttons = document.querySelectorAll('.test-btn');
  buttons.forEach(btn => btn.classList.remove('active'));
  event?.target?.classList.add('active');

  try {
    const res = await fetch('/api/simulator/scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario, workerId: 'MW-0742' })
    });
    const json = await res.json();
    if (json.activeData) updateUI(json.activeData);
  } catch (e) {
    console.error("Error triggering scenario:", e);
  }
}

// DOM Init
document.addEventListener('DOMContentLoaded', () => {
  initChart();
  initWebSocket();

  const sirenBtn = document.getElementById('siren-toggle-btn');
  if (sirenBtn) {
    sirenBtn.addEventListener('click', () => {
      initAudio();
      isAudioEnabled = !isAudioEnabled;
      const text = document.getElementById('siren-text');
      const icon = document.getElementById('siren-icon');
      if (isAudioEnabled) {
        text.innerText = 'Alarm Sound: ON';
        icon.innerText = '🔊';
      } else {
        text.innerText = 'Alarm Sound: MUTED';
        icon.innerText = '🔇';
      }
    });
  }
});
