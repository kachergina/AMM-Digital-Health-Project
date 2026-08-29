"""Data processing for the AMM Digital System.

This module analyzes SIMULATED sensor readings only. It is a conceptual
demonstration for a student portfolio and is NOT a medical device.

It must never be presented as medical diagnosis, medical advice, or a
clinically validated risk assessment. No machine learning is used.
"""

DISCLAIMER = (
    "SIMULATED DATA — not a real medical device. "
    "Do not use for diagnosis or treatment."
)

# Illustrative reference ranges for the demo.
# These are simple, clearly named constants so the logic stays easy to read.
# They are NOT clinically validated medical thresholds.
TEMPERATURE_RANGE = (36.0, 37.5)        # degrees Celsius
HEART_RATE_RANGE = (60, 100)            # beats per minute
SPO2_RANGE = (95, 100)                  # percent
RESPIRATORY_RATE_RANGE = (12, 20)       # breaths per minute

# One place that describes every vital we know about.
REFERENCE_RANGES = {
    "temperature_c": {
        "label": "Body temperature",
        "unit": "°C",
        "low": TEMPERATURE_RANGE[0],
        "high": TEMPERATURE_RANGE[1],
    },
    "heart_rate_bpm": {
        "label": "Heart rate",
        "unit": "bpm",
        "low": HEART_RATE_RANGE[0],
        "high": HEART_RATE_RANGE[1],
    },
    "spo2_percent": {
        "label": "Blood oxygen (SpO2)",
        "unit": "%",
        "low": SPO2_RANGE[0],
        "high": SPO2_RANGE[1],
    },
    "respiratory_rate_bpm": {
        "label": "Respiratory rate",
        "unit": "breaths/min",
        "low": RESPIRATORY_RATE_RANGE[0],
        "high": RESPIRATORY_RATE_RANGE[1],
    },
}

# Overall simulated status values.
STATUS_NORMAL = "NORMAL"
STATUS_ATTENTION = "ATTENTION"
STATUS_REVIEW = "REVIEW"
STATUS_INVALID = "INVALID"


def _is_number(value):
    """Return True only for int or float, but not for booleans."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def analyze_vital(name, value):
    """Compare one simulated vital against its illustrative range.

    Returns a small dictionary describing the result. The status is one of
    WITHIN, BELOW or ABOVE the configured range.
    """
    config = REFERENCE_RANGES[name]
    low = config["low"]
    high = config["high"]

    if value < low:
        status = "BELOW"
    elif value > high:
        status = "ABOVE"
    else:
        status = "WITHIN"

    return {
        "name": name,
        "label": config["label"],
        "value": value,
        "unit": config["unit"],
        "low": low,
        "high": high,
        "status": status,
    }


def _overall_status(outside_count):
    """Turn a count of out-of-range vitals into an overall simulated status.

    This is a simple, transparent rule for the demo only:
      - 0 out of range -> NORMAL
      - 1 out of range -> ATTENTION
      - 2 or more     -> REVIEW
    """
    if outside_count == 0:
        return STATUS_NORMAL
    if outside_count == 1:
        return STATUS_ATTENTION
    return STATUS_REVIEW


def analyze_reading(reading):
    """Analyze one simulated sensor reading.

    The input is expected to be a dictionary produced by the simulator.
    The function is safe: missing or non-numeric fields do not crash the
    program, they produce an INVALID result instead.

    Returns a structured dictionary with the overall status and per-vital
    analysis. Every result is clearly marked as simulated.
    """
    if not isinstance(reading, dict):
        return _error_result("reading is not a dictionary")

    missing = [name for name in REFERENCE_RANGES if name not in reading]
    if missing:
        return _error_result("missing fields: " + ", ".join(missing))

    vitals = []
    outside_count = 0
    for name in REFERENCE_RANGES:
        value = reading[name]
        if not _is_number(value):
            return _error_result(f"field '{name}' is not a number")
        result = analyze_vital(name, value)
        if result["status"] != "WITHIN":
            outside_count += 1
        vitals.append(result)

    return {
        "simulated": True,
        "disclaimer": DISCLAIMER,
        "overall_status": _overall_status(outside_count),
        "vitals": vitals,
    }


def _error_result(message):
    """Build a safe result when the input reading cannot be analyzed."""
    return {
        "simulated": True,
        "disclaimer": DISCLAIMER,
        "overall_status": STATUS_INVALID,
        "error": message,
        "vitals": [],
    }
