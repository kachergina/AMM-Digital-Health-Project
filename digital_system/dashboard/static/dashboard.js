/* AMM Digital System — dashboard behaviour (simulation only).

This script fetches SIMULATED data from the local Flask API and updates the
page. It never sends or receives real patient data.

Charts are drawn with the browser's built-in Canvas API so the dashboard has
no external dependencies and works fully offline.
*/

(function () {
  "use strict";

  var MAX_POINTS = 10;
  var MAX_HISTORY = 30;

  var temperatureData = [];
  var heartData = [];
  var spo2Data = [];
  var respData = [];
  var sessionHistory = [];
  var autoTimer = null;
  var demoScenario = null;

  var statusClass = {
    NORMAL: "state-normal",
    ATTENTION: "state-attention",
    REVIEW: "state-review",
    INVALID: "state-invalid",
    WITHIN: "state-within",
    BELOW: "state-below",
    ABOVE: "state-above"
  };

  function el(id) {
    return document.getElementById(id);
  }

  function shortTime(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    return d.toLocaleTimeString();
  }

  function setStatusBadge(elementId, status) {
    var node = el(elementId);
    if (!node) return;
    node.textContent = status;
    node.className = "vital-status";
    if (statusClass[status]) node.classList.add(statusClass[status]);
  }

  function updateVital(name, value, statusCode, statusLabel) {
    var valueNode = el("value-" + name);
    if (valueNode) valueNode.textContent = value;
    setStatusBadge("status-" + name, statusCode);
    var badge = el("status-" + name);
    if (badge && statusLabel) badge.textContent = statusLabel;
    var card = el("card-" + name);
    if (card) {
      card.className = "vital-card";
      if (statusClass[statusCode]) card.classList.add(statusClass[statusCode]);
    }
  }

  function drawLineChart(canvas, data, color, low, high) {
    if (!canvas) return;
    var ctx = canvas.getContext && canvas.getContext("2d");
    if (!ctx) return;

    var cssWidth = canvas.clientWidth || 300;
    var cssHeight = canvas.clientHeight || 240;
    var dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(cssWidth * dpr);
    canvas.height = Math.round(cssHeight * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cssWidth, cssHeight);

    var padL = 40, padR = 14, padT = 14, padB = 26;
    var plotW = cssWidth - padL - padR;
    var plotH = cssHeight - padT - padB;

    if (data.length === 0) return;

    var lo = (typeof low === "number") ? low : null;
    var hi = (typeof high === "number") ? high : null;
    var min = Math.min.apply(null, data);
    var max = Math.max.apply(null, data);
    if (lo !== null) min = Math.min(min, lo);
    if (hi !== null) max = Math.max(max, hi);
    if (min === max) { min -= 1; max += 1; }
    var range = max - min;
    min -= range * 0.1;
    max += range * 0.1;
    range = max - min;

    function xFor(idx) {
      return padL + plotW * (idx / Math.max(1, data.length - 1));
    }
    function yFor(v) {
      return padT + plotH * ((max - v) / range);
    }

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, cssWidth, cssHeight);

    if (lo !== null && hi !== null) {
      ctx.fillStyle = "rgba(31,157,107,0.12)";
      ctx.fillRect(padL, yFor(hi), plotW, yFor(lo) - yFor(hi));
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = "rgba(31,157,107,0.55)";
      ctx.lineWidth = 1;
      [hi, lo].forEach(function (v) {
        ctx.beginPath();
        ctx.moveTo(padL, yFor(v));
        ctx.lineTo(padL + plotW, yFor(v));
        ctx.stroke();
      });
      ctx.restore();
    }

    ctx.strokeStyle = "#e3edf7";
    ctx.fillStyle = "#9aa6b2";
    ctx.font = "11px Inter, sans-serif";
    ctx.lineWidth = 1;
    var steps = 4;
    for (var i = 0; i <= steps; i++) {
      var y = padT + (plotH * i) / steps;
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(padL + plotW, y);
      ctx.stroke();
      var label = (max - range * (i / steps)).toFixed(0);
      ctx.fillText(label, 6, y + 4);
    }

    if (data.length > 1) {
      ctx.beginPath();
      ctx.moveTo(xFor(0), yFor(data[0]));
      for (var j = 1; j < data.length; j++) ctx.lineTo(xFor(j), yFor(data[j]));
      ctx.lineTo(xFor(data.length - 1), padT + plotH);
      ctx.lineTo(xFor(0), padT + plotH);
      ctx.closePath();
      ctx.fillStyle = color + "22";
      ctx.fill();
    }

    ctx.beginPath();
    ctx.moveTo(xFor(0), yFor(data[0]));
    for (var k = 1; k < data.length; k++) ctx.lineTo(xFor(k), yFor(data[k]));
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = color;
    for (var p = 0; p < data.length; p++) {
      ctx.beginPath();
      ctx.arc(xFor(p), yFor(data[p]), 2.5, 0, Math.PI * 2);
      ctx.fill();
    }

    var last = data.length - 1;
    var lx = xFor(last), ly = yFor(data[last]);
    ctx.beginPath();
    ctx.arc(lx, ly, 6.5, 0, Math.PI * 2);
    ctx.fillStyle = color + "22";
    ctx.fill();
    ctx.beginPath();
    ctx.arc(lx, ly, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  function pushPoint(canvas, store, value, color, low, high) {
    store.push(value);
    if (store.length > MAX_POINTS) store.shift();
    drawLineChart(canvas, store, color, low, high);
  }

  function applyReading(data) {
    var reading = data.reading;
    var analysis = data.analysis;

    el("reading-timestamp").textContent = shortTime(reading.timestamp);

    setMonitorState();

    var overall = analysis.overall_status;
    var overallNode = el("overall-status");
    overallNode.textContent = analysis.overall_status_label || overall;
    var card = el("overall-status-card");
    card.className = "status-card";
    if (statusClass[overall]) card.classList.add(statusClass[overall]);

    analysis.vitals.forEach(function (v) {
      updateVital(v.name, v.value, v.status, v.status_label);
    });

    var bands = {};
    analysis.vitals.forEach(function (v) { bands[v.name] = v; });
    pushPoint(el("temp-chart"), temperatureData, reading.temperature_c, "#e07b39",
              bands.temperature_c.low, bands.temperature_c.high);
    pushPoint(el("heart-chart"), heartData, reading.heart_rate_bpm, "#4a9eed",
              bands.heart_rate_bpm.low, bands.heart_rate_bpm.high);
    pushPoint(el("spo2-chart"), spo2Data, reading.spo2_percent, "#1f9d6b",
              bands.spo2_percent.low, bands.spo2_percent.high);
    pushPoint(el("resp-chart"), respData, reading.respiratory_rate_bpm, "#7c5cff",
              bands.respiratory_rate_bpm.low, bands.respiratory_rate_bpm.high);

    sessionHistory.push({ reading: reading, analysis: analysis });
    if (sessionHistory.length > MAX_HISTORY) sessionHistory.shift();
    updateAlert(analysis);
    addEvent(data);
    updatePipelineDetails(data);

    pulsePipeline();
  }

  function addEvent(data) {
    var analysis = data.analysis;
    if (!analysis || analysis.overall_status === "NORMAL" ||
        analysis.overall_status === "INVALID") return;
    var list = el("events-list");
    if (!list) return;
    var i18n = window.AMM_I18N || {};
    var tripped = analysis.vitals
      .filter(function (v) { return v.status !== "WITHIN"; })
      .map(function (v) { return v.label + " " + v.status_label; });
    var scenarioKey = data.scenario || "normal";
    var scenarioLabel = (i18n.scenarios && i18n.scenarios[scenarioKey]) || scenarioKey;
    var li = document.createElement("li");
    li.className = "event-item " + (statusClass[analysis.overall_status] || "");
    li.textContent = shortTime(data.reading.timestamp) + " · " + scenarioLabel +
                     " · " + tripped.join(", ");
    list.insertBefore(li, list.firstChild);
    while (list.children.length > 12) list.removeChild(list.lastChild);
  }

  function updatePipelineDetails(data) {
    var reading = data.reading;
    var analysis = data.analysis;
    var i18n = window.AMM_I18N || {};

    var sensors = el("detail-sensors");
    if (sensors) {
      sensors.textContent = reading.temperature_c + "°C · " + reading.heart_rate_bpm +
        " bpm · " + reading.spo2_percent + "% · " + reading.respiratory_rate_bpm + " rpm";
    }
    var proc = el("detail-processing");
    if (proc) {
      var outside = analysis.vitals.filter(function (v) { return v.status !== "WITHIN"; }).length;
      proc.textContent = outside + " · " + (analysis.overall_status_label || analysis.overall_status);
    }
    var api = el("detail-api");
    if (api) {
      var lang = document.body.dataset.lang || "en";
      var scenario = demoScenario || "normal";
      api.textContent = "/api/vitals?lang=" + lang + "&scenario=" + scenario;
    }
    var dash = el("detail-dashboard");
    if (dash) dash.textContent = i18n.detail_dashboard || "rendered";
  }

  function updateAlert(analysis) {
    var banner = el("alert-banner");
    var statusNode = el("alert-status");
    var msgNode = el("alert-message");
    if (!banner) return;
    var status = analysis.overall_status;
    var i18n = window.AMM_I18N || {};
    statusNode.textContent = analysis.overall_status_label || status;
    msgNode.textContent = i18n["alert_" + status.toLowerCase()] || "";
    banner.className = "alert-banner";
    if (statusClass[status]) banner.classList.add(statusClass[status]);
  }

  function renderComponents(components) {
    var list = el("components-list");
    if (!list) return;
    list.innerHTML = "";
    components.forEach(function (c) {
      var li = document.createElement("li");
      li.className = "component-item";

      var name = document.createElement("span");
      name.className = "component-name";
      name.textContent = c.name;

      var role = document.createElement("span");
      role.className = "component-role";
      role.textContent = c.role;

      var state = document.createElement("span");
      state.className = "component-state online";
      state.textContent = c.state;

      li.appendChild(name);
      li.appendChild(role);
      li.appendChild(state);
      list.appendChild(li);
    });
  }

  function apiUrl(path) {
    var lang = document.body.dataset.lang || "en";
    return path + "?lang=" + encodeURIComponent(lang);
  }

  function loadSystem() {
    fetch(apiUrl("/api/status"))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.components) renderComponents(data.components);
      })
      .catch(function (err) {
        console.error("Status fetch failed:", err);
      });
  }

  function pulseStage(id, delay) {
    setTimeout(function () {
      var stage = el(id);
      if (!stage) return;
      stage.classList.add("stage-active");
      setTimeout(function () { stage.classList.remove("stage-active"); }, 600);
    }, delay);
  }

  function pulsePipeline() {
    pulseStage("stage-sensors", 0);
    pulseStage("stage-processing", 150);
    pulseStage("stage-api", 300);
    pulseStage("stage-dashboard", 450);
  }

  function runSimulation() {
    var url = apiUrl("/api/vitals");
    if (demoScenario) url += "&scenario=" + encodeURIComponent(demoScenario);
    fetch(url)
      .then(function (res) { return res.json(); })
      .then(applyReading)
      .catch(function (err) {
        console.error("Simulation fetch failed:", err);
      });
  }

  function setAuto(on) {
    var btn = el("auto-button");
    var i18n = window.AMM_I18N || {};
    if (on) {
      if (!autoTimer) autoTimer = setInterval(runSimulation, 5000);
      btn.textContent = i18n.auto_on || "Auto refresh: on";
      btn.setAttribute("aria-pressed", "true");
    } else {
      if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
      btn.textContent = i18n.auto_off || "Auto refresh: off";
      btn.setAttribute("aria-pressed", "false");
    }
  }

  function toggleDemoPanel() {
    var panel = el("demo-panel");
    if (!panel) return;
    panel.hidden = !panel.hidden;
    el("demo-toggle").setAttribute("aria-expanded", String(!panel.hidden));
  }

  function setMonitorState() {
    var pill = el("monitor-pill");
    var state = el("monitor-state");
    var i18n = window.AMM_I18N || {};
    if (!state) return;
    if (demoScenario) {
      var label = (i18n.scenarios && i18n.scenarios[demoScenario]) || demoScenario;
      state.textContent = (i18n.demo_mode || "Demo Mode") + " · " + label;
      if (pill) pill.classList.add("is-demo");
    } else {
      state.textContent = i18n.live_monitoring || "Live monitoring (simulated)";
      if (pill) pill.classList.remove("is-demo");
    }
  }

  function selectDemo(scenario) {
    demoScenario = scenario;
    var panel = el("demo-panel");
    if (panel) panel.hidden = true;
    var toggle = el("demo-toggle");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
    Array.prototype.forEach.call(document.querySelectorAll(".btn-demo"), function (b) {
      b.classList.toggle("active", b.getAttribute("data-scenario") === scenario);
    });
    setMonitorState();
    runSimulation();
  }

  function downloadFile(filename, text, mime) {
    var blob = new Blob([text], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function exportSession(format) {
    if (sessionHistory.length === 0) return;
    var header = ["timestamp", "temperature_c", "heart_rate_bpm",
                  "spo2_percent", "respiratory_rate_bpm", "overall_status"];
    if (format === "csv") {
      var rows = [header.join(",")];
      sessionHistory.forEach(function (item) {
        var r = item.reading;
        rows.push([
          r.timestamp, r.temperature_c, r.heart_rate_bpm,
          r.spo2_percent, r.respiratory_rate_bpm, item.analysis.overall_status
        ].join(","));
      });
      downloadFile("amm-session.csv", rows.join("\n"), "text/csv");
    } else {
      downloadFile("amm-session.json", JSON.stringify(sessionHistory, null, 2),
                   "application/json");
    }
  }

  function init() {
    el("run-button").addEventListener("click", runSimulation);
    el("auto-button").addEventListener("click", function () { setAuto(!autoTimer); });
    el("export-json").addEventListener("click", function () { exportSession("json"); });
    el("export-csv").addEventListener("click", function () { exportSession("csv"); });
    el("demo-toggle").addEventListener("click", toggleDemoPanel);
    Array.prototype.forEach.call(document.querySelectorAll(".btn-demo"), function (b) {
      b.addEventListener("click", function () { selectDemo(b.getAttribute("data-scenario")); });
    });
    el("demo-exit").addEventListener("click", function () { selectDemo(null); });
    loadSystem();
    setAuto(true);
    runSimulation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
