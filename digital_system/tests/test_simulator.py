"""Tests for the AMM Digital System sensor simulator.

Run them from the digital_system/ folder with:  pytest
"""

from simulator.sensors import SIMULATED_FLAG, SensorSimulator, generate_reading
from processing.analyze import analyze_reading

EXPECTED_KEYS = (
    "timestamp",
    "simulated",
    "note",
    "temperature_c",
    "heart_rate_bpm",
    "spo2_percent",
    "respiratory_rate_bpm",
)


def test_generate_reading_has_required_keys():
    reading = generate_reading()
    for key in EXPECTED_KEYS:
        assert key in reading


def test_generate_reading_is_marked_simulated():
    reading = generate_reading()
    assert reading["simulated"] is True
    assert reading["note"] == SIMULATED_FLAG


def test_timestamp_is_a_non_empty_string():
    reading = generate_reading()
    assert isinstance(reading["timestamp"], str)
    assert "T" in reading["timestamp"]


def test_temperature_in_realistic_range():
    for _ in range(50):
        value = generate_reading()["temperature_c"]
        assert 35.0 <= value <= 39.0


def test_heart_rate_in_realistic_range():
    for _ in range(50):
        value = generate_reading()["heart_rate_bpm"]
        assert 40 <= value <= 120


def test_spo2_in_realistic_range():
    for _ in range(50):
        value = generate_reading()["spo2_percent"]
        assert 90 <= value <= 100


def test_respiratory_rate_in_realistic_range():
    for _ in range(50):
        value = generate_reading()["respiratory_rate_bpm"]
        assert 8 <= value <= 30


def test_readings_vary_between_calls():
    temperatures = {generate_reading()["temperature_c"] for _ in range(30)}
    assert len(temperatures) > 1


def test_sensor_simulator_read_many():
    simulator = SensorSimulator()
    readings = simulator.read_many(5)
    assert len(readings) == 5
    for reading in readings:
        assert reading["simulated"] is True
        for key in EXPECTED_KEYS:
            assert key in reading


def test_scenarios_constant_has_five_presets():
    from simulator.sensors import SCENARIOS
    assert SCENARIOS == ("normal", "fever", "low_spo2", "tachycardia", "critical")


def test_fever_scenario_elevates_temperature():
    for _ in range(20):
        reading = generate_reading("fever")
        assert reading["temperature_c"] > 37.5


def test_low_spo2_scenario_lowers_spo2():
    for _ in range(20):
        reading = generate_reading("low_spo2")
        assert reading["spo2_percent"] < 95


def test_tachycardia_scenario_raises_heart_rate():
    for _ in range(20):
        reading = generate_reading("tachycardia")
        assert reading["heart_rate_bpm"] > 100


def test_critical_scenario_is_multi_abnormal():
    for _ in range(20):
        reading = generate_reading("critical")
        outside = sum([
            reading["temperature_c"] > 37.5,
            reading["spo2_percent"] < 95,
            reading["heart_rate_bpm"] > 100,
            reading["respiratory_rate_bpm"] > 20,
        ])
        assert outside >= 2


def test_invalid_scenario_falls_back_to_normal():
    reading = generate_reading("not_a_real_scenario")
    assert reading["simulated"] is True
    for key in EXPECTED_KEYS:
        assert key in reading
    assert 35.0 <= reading["temperature_c"] <= 39.0


def test_scenario_is_abnormal_on_first_call():
    # Switching scenario must snap to the target immediately (coherent demo).
    for scenario in ("fever", "low_spo2", "tachycardia", "critical"):
        reading = generate_reading(scenario)
        assert analyze_reading(reading)["overall_status"] in ("ATTENTION", "REVIEW")


def test_vitals_stay_coherent_within_scenario():
    # A fever should also lift heart rate / respiratory rate, not just temperature.
    reading = generate_reading("fever")
    assert reading["heart_rate_bpm"] > 100
    # Fever target resp is 21; the snap can land on 20, so tolerate the boundary.
    assert reading["respiratory_rate_bpm"] >= 20


def test_consecutive_readings_drift_within_scenario():
    readings = [generate_reading("normal") for _ in range(12)]
    temps = [r["temperature_c"] for r in readings]
    # Drift + noise means not every reading is identical.
    assert len(set(temps)) > 1
