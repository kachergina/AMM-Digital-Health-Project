"""API routes for the AMM Digital System.

This module defines the Flask routes. Every response contains only SIMULATED
data and repeats the disclaimer that this is not a real medical device.

All user-facing text is localized through digital_system.i18n; the underlying
data and logic (sensor names, units, status codes) stay language-neutral.
"""

import os

from flask import Blueprint, Response, jsonify, render_template, request, send_file

from simulator.sensors import generate_reading, SCENARIOS
from processing.analyze import analyze_reading
from i18n import get_strings

api_bp = Blueprint("api", __name__)

# Project root is two levels above digital_system/api/; reuse the EXISTING
# public-site favicon asset rather than creating a new icon.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAVICON_SVG = os.path.join(PROJECT_ROOT, "assets", "images", "favicon.svg")
FAVICON_ICO = os.path.join(PROJECT_ROOT, "assets", "images", "favicon.ico")

AMM_COMPONENTS = [
    {"name": "Thermal camera", "role": "Estimates body temperature from a non-contact thermal image (simulated)."},
    {"name": "LiDAR scanner", "role": "Builds a 3D body map for non-contact assessment (simulated)."},
    {"name": "Medical sensors", "role": "Produce heart rate, SpO2 and respiratory rate signals (simulated)."},
    {"name": "Robotic manipulator", "role": "Planned contact procedures under doctor control (simulated, idle)."},
    {"name": "UV sterilisation", "role": "Module disinfection between patients (simulated, idle)."},
]

PIPELINE_STAGES = ["Sensors", "Processing", "API", "Dashboard"]


def _lang():
    """Read the requested language from the query string, defaulting to English."""
    return request.args.get("lang", "en")


def _localize_analysis(analysis, strings):
    """Return a copy of the analysis with localized labels; codes stay intact."""
    result = dict(analysis)
    result["overall_status_label"] = strings["status"].get(
        analysis["overall_status"], analysis["overall_status"]
    )
    vitals = []
    for vital in analysis["vitals"]:
        v = dict(vital)
        v["label"] = strings["vitals"].get(vital["name"], vital["label"])
        v["status_label"] = strings["vital_status"].get(vital["status"], vital["status"])
        vitals.append(v)
    result["vitals"] = vitals
    return result


def _localize_components(strings):
    out = []
    for component in AMM_COMPONENTS:
        out.append({
            "name": strings["component_names"].get(component["name"], component["name"]),
            "role": strings["component_roles"].get(component["name"], component["role"]),
            "state": strings["component_state"],
        })
    return out


@api_bp.route("/")
def dashboard():
    """Serve the AMM Digital System dashboard (simulation only)."""
    lang = _lang()
    if lang not in ("en", "fr", "ru"):
        lang = "en"
    return render_template("index.html", lang=lang, strings=get_strings(lang))


@api_bp.route("/api/vitals")
def vitals():
    """Generate one simulated reading, process it, and return both as JSON.

    An optional ?scenario=normal|fever|low_spo2|tachycardia|critical selects a
    preset; unknown values fall back to "normal".
    """
    strings = get_strings(_lang())
    scenario = request.args.get("scenario", "normal")
    if scenario not in SCENARIOS:
        scenario = "normal"
    reading = generate_reading(scenario)
    analysis = _localize_analysis(analyze_reading(reading), strings)
    payload = {
        "simulated": True,
        "disclaimer": strings["disclaimer_api"],
        "scenario": scenario,
        "reading": reading,
        "analysis": analysis,
    }
    return jsonify(payload)


@api_bp.route("/api/status")
def status():
    """Return the current simulated AMM system status as JSON."""
    strings = get_strings(_lang())
    payload = {
        "simulated": True,
        "disclaimer": strings["disclaimer_api"],
        "system": "AMM Digital System",
        "state": strings["system_state"],
        "pipeline": list(PIPELINE_STAGES),
        "sensors": [
            "temperature_c",
            "heart_rate_bpm",
            "spo2_percent",
            "respiratory_rate_bpm",
        ],
        "components": _localize_components(strings),
        "possible_statuses": list(strings["status"].keys()),
    }
    return jsonify(payload)


@api_bp.route("/favicon.svg")
def favicon_svg():
    """Serve the existing AMM favicon (svg) for the dashboard browser tab."""
    # Return the SVG with a clean Content-Type. Flask normally appends
    # "; charset=utf-8" to image/svg+xml, and Chromium ignores SVG favicons
    # that carry a charset parameter, so force the header without charset.
    with open(FAVICON_SVG, "rb") as fh:
        resp = Response(fh.read(), mimetype="image/svg+xml")
    resp.headers["Content-Type"] = "image/svg+xml"
    return resp


@api_bp.route("/favicon.ico")
def favicon_ico():
    """Serve the existing AMM favicon (ico) for the dashboard browser tab."""
    return send_file(FAVICON_ICO, mimetype="image/x-icon")
