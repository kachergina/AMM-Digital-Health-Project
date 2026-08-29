"""Tests for the AMM Digital System data processing layer.

Run them from the digital_system/ folder with:  pytest
"""

from processing.analyze import (
    STATUS_NORMAL,
    STATUS_ATTENTION,
    STATUS_REVIEW,
    STATUS_INVALID,
    analyze_reading,
    analyze_vital,
)


def _normal_reading():
    """Build a reading where every vital is inside its illustrative range."""
    return {
        "temperature_c": 36.8,
        "heart_rate_bpm": 75,
        "spo2_percent": 98,
        "respiratory_rate_bpm": 16,
    }


def test_analyze_vital_inside_range():
    result = analyze_vital("heart_rate_bpm", 75)
    assert result["status"] == "WITHIN"
    assert result["low"] == 60
    assert result["high"] == 100


def test_analyze_vital_below_range():
    result = analyze_vital("spo2_percent", 90)
    assert result["status"] == "BELOW"


def test_analyze_vital_above_range():
    result = analyze_vital("temperature_c", 39.0)
    assert result["status"] == "ABOVE"


def test_valid_reading_is_normal():
    result = analyze_reading(_normal_reading())
    assert result["overall_status"] == STATUS_NORMAL
    assert len(result["vitals"]) == 4
    assert result["simulated"] is True
    assert "disclaimer" in result


def test_one_outside_range_is_attention():
    reading = _normal_reading()
    reading["heart_rate_bpm"] = 130
    result = analyze_reading(reading)
    assert result["overall_status"] == STATUS_ATTENTION


def test_two_outside_range_is_review():
    reading = _normal_reading()
    reading["heart_rate_bpm"] = 130
    reading["spo2_percent"] = 88
    result = analyze_reading(reading)
    assert result["overall_status"] == STATUS_REVIEW


def test_missing_field_is_handled_safely():
    reading = _normal_reading()
    del reading["temperature_c"]
    result = analyze_reading(reading)
    assert result["overall_status"] == STATUS_INVALID
    assert "error" in result


def test_non_numeric_field_is_handled_safely():
    reading = _normal_reading()
    reading["heart_rate_bpm"] = "fast"
    result = analyze_reading(reading)
    assert result["overall_status"] == STATUS_INVALID
    assert "error" in result


def test_non_dict_input_is_handled_safely():
    result = analyze_reading("not a dictionary")
    assert result["overall_status"] == STATUS_INVALID
