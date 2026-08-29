"""Simulated sensor data for the AMM Digital System.

This module generates FAKE patient measurements to demonstrate the AMM concept.
It does NOT read from real medical devices and must NOT be used for diagnosis
or treatment of any kind.

All values are random numbers kept inside realistic human ranges so the demo
looks plausible while remaining clearly a simulation.
"""

import random
from datetime import datetime, timezone

SIMULATED_FLAG = "SIMULATED — not real patient data"

# Demo scenarios the simulator can produce. "normal" is the default; the others
# push one or more vitals outside the illustrative reference ranges so the
# detection/alerting can be demonstrated on demand.
SCENARIOS = ("normal", "fever", "low_spo2", "tachycardia", "critical")

# Target values per scenario. Scenarios are coherent: a fever also raises heart
# rate and respiratory rate, hypoxia raises respiratory rate, etc. This makes
# the simulation look like a believable patient rather than unrelated noise.
_TARGETS = {
    "normal": (36.8, 76, 98, 15),
    "fever": (39.2, 104, 97, 21),
    "low_spo2": (36.7, 92, 87, 22),
    "tachycardia": (36.8, 130, 97, 19),
    "critical": (39.5, 140, 85, 29),
}

# Process-global state so consecutive readings drift smoothly (a small random
# walk) like a live monitor. Switching scenario snaps to the new target so the
# abnormality appears immediately and stays coherent.
_STATE = {
    "temperature_c": 36.8,
    "heart_rate_bpm": 76,
    "spo2_percent": 98,
    "respiratory_rate_bpm": 15,
}
_STATE_SCENARIO = "normal"


def _round(value, digits):
    """Round a number to the given number of decimal digits."""
    return round(value, digits)


def generate_reading(scenario="normal"):
    """Create one simulated sensor reading as a dictionary.

    The dictionary always contains:
      - timestamp: when the reading was created (ISO 8601 string, UTC)
      - simulated: True, to mark the data as not real
      - note: a human-readable warning that the data is simulated
      - temperature_c: body temperature in degrees Celsius
      - heart_rate_bpm: heart rate in beats per minute
      - spo2_percent: blood oxygen saturation in percent
      - respiratory_rate_bpm: respiratory rate in breaths per minute

    The optional `scenario` selects a preset (see SCENARIOS); unknown values
    fall back to "normal". Values drift smoothly between calls and related
    vitals move together so the scenario looks physiologically coherent.
    """
    if scenario not in SCENARIOS:
        scenario = "normal"
    temp_t, hr_t, spo2_t, resp_t = _TARGETS[scenario]
    global _STATE, _STATE_SCENARIO
    if scenario != _STATE_SCENARIO:
        # Snap to the new scenario so the abnormality is immediate and coherent.
        _STATE = {
            "temperature_c": _round(temp_t + random.uniform(-0.2, 0.2), 1),
            "heart_rate_bpm": int(round(hr_t + random.uniform(-3, 3))),
            "spo2_percent": int(round(spo2_t + random.uniform(-1, 1))),
            "respiratory_rate_bpm": int(round(resp_t + random.uniform(-1, 1))),
        }
        _STATE_SCENARIO = scenario
    else:
        # Smooth drift: ease current values toward the target plus small noise.
        _STATE["temperature_c"] = _round(
            _STATE["temperature_c"] + 0.15 * (temp_t - _STATE["temperature_c"])
            + random.uniform(-0.15, 0.15), 1)
        _STATE["heart_rate_bpm"] = int(round(
            _STATE["heart_rate_bpm"] + 0.15 * (hr_t - _STATE["heart_rate_bpm"])
            + random.uniform(-2, 2)))
        _STATE["spo2_percent"] = int(round(
            _STATE["spo2_percent"] + 0.15 * (spo2_t - _STATE["spo2_percent"])
            + random.uniform(-0.8, 0.8)))
        _STATE["respiratory_rate_bpm"] = int(round(
            _STATE["respiratory_rate_bpm"] + 0.15 * (resp_t - _STATE["respiratory_rate_bpm"])
            + random.uniform(-1, 1)))
    # Keep values inside safe, plausible bounds.
    _STATE["temperature_c"] = min(max(_STATE["temperature_c"], 35.0), 41.0)
    _STATE["heart_rate_bpm"] = min(max(_STATE["heart_rate_bpm"], 40), 160)
    _STATE["spo2_percent"] = min(max(_STATE["spo2_percent"], 70), 100)
    _STATE["respiratory_rate_bpm"] = min(max(_STATE["respiratory_rate_bpm"], 6), 35)
    now = datetime.now(timezone.utc)
    return {
        "timestamp": now.isoformat(),
        "simulated": True,
        "note": SIMULATED_FLAG,
        "temperature_c": _STATE["temperature_c"],
        "heart_rate_bpm": _STATE["heart_rate_bpm"],
        "spo2_percent": _STATE["spo2_percent"],
        "respiratory_rate_bpm": _STATE["respiratory_rate_bpm"],
    }


class SensorSimulator:
    """Generates a stream of simulated AMM sensor readings.

    Using a small class keeps the code easy to extend later (for example to
    add more sensors) without changing how the rest of the project calls it.
    """

    def __init__(self):
        self.simulated = True

    def read(self, scenario="normal"):
        """Return a single simulated reading (optionally for a scenario)."""
        return generate_reading(scenario)

    def read_many(self, count, scenario="normal"):
        """Return a list of `count` simulated readings (optionally for a scenario)."""
        return [generate_reading(scenario) for _ in range(count)]
