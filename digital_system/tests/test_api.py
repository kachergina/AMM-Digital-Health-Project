"""Tests for the AMM Digital System Flask API.

Run them from the digital_system/ folder with:  pytest
"""

from app import create_app
from processing.analyze import (
    STATUS_NORMAL,
    STATUS_ATTENTION,
    STATUS_REVIEW,
    STATUS_INVALID,
)

EXPECTED_VITALS = {
    "temperature_c",
    "heart_rate_bpm",
    "spo2_percent",
    "respiratory_rate_bpm",
}


def test_api_vitals_returns_200(client):
    response = client.get("/api/vitals")
    assert response.status_code == 200


def test_api_vitals_structure(client):
    response = client.get("/api/vitals")
    data = response.get_json()
    assert data["simulated"] is True
    assert "disclaimer" in data
    assert "reading" in data
    assert "analysis" in data
    assert EXPECTED_VITALS.issubset(set(data["reading"].keys()))


def test_api_vitals_analysis_is_valid(client):
    response = client.get("/api/vitals")
    data = response.get_json()
    status = data["analysis"]["overall_status"]
    assert status in (STATUS_NORMAL, STATUS_ATTENTION, STATUS_REVIEW, STATUS_INVALID)


def test_api_status_returns_200(client):
    response = client.get("/api/status")
    assert response.status_code == 200


def test_api_status_structure(client):
    response = client.get("/api/status")
    data = response.get_json()
    assert data["simulated"] is True
    assert "disclaimer" in data
    assert data["system"] == "AMM Digital System"
    assert data["state"].startswith("ONLINE")
    assert set(data["sensors"]) == EXPECTED_VITALS


def test_api_status_includes_pipeline(client):
    response = client.get("/api/status")
    data = response.get_json()
    assert data["pipeline"] == ["Sensors", "Processing", "API", "Dashboard"]


def test_api_status_includes_components(client):
    response = client.get("/api/status")
    data = response.get_json()
    assert isinstance(data["components"], list)
    assert len(data["components"]) >= 3
    first = data["components"][0]
    for key in ("name", "role", "state"):
        assert key in first
    names = {c["name"] for c in data["components"]}
    assert "Thermal camera" in names
    assert "Medical sensors" in names


def test_api_vitals_french_localized(client):
    response = client.get("/api/vitals?lang=fr")
    data = response.get_json()
    assert data["analysis"]["overall_status_label"] in ("Normal", "Attention", "À vérifier", "Invalide")
    labels = {v["name"]: v["label"] for v in data["analysis"]["vitals"]}
    assert labels["heart_rate_bpm"] == "Fréquence cardiaque"
    assert data["disclaimer"] != "SIMULATED DATA — not a real medical device. Do not use for diagnosis or treatment."


def test_api_vitals_russian_localized(client):
    response = client.get("/api/vitals?lang=ru")
    data = response.get_json()
    labels = {v["name"]: v["label"] for v in data["analysis"]["vitals"]}
    assert labels["heart_rate_bpm"] == "Частота пульса"
    assert labels["spo2_percent"] == "Уровень кислорода (SpO₂)"


def test_api_vitals_invalid_lang_falls_back_to_english(client):
    response = client.get("/api/vitals?lang=xx")
    data = response.get_json()
    labels = {v["name"]: v["label"] for v in data["analysis"]["vitals"]}
    assert labels["heart_rate_bpm"] == "Heart rate"
    assert data["disclaimer"] == "SIMULATED DATA — not a real medical device. Do not use for diagnosis or treatment."


def test_api_status_french_components_localized(client):
    response = client.get("/api/status?lang=fr")
    data = response.get_json()
    names = {c["name"] for c in data["components"]}
    assert "Caméra thermique" in names
    assert data["state"] == "EN LIGNE (simulation)"


def test_api_vitals_scenario_fever_is_abnormal(client):
    response = client.get("/api/vitals?scenario=fever&lang=en")
    data = response.get_json()
    assert data["scenario"] == "fever"
    assert data["reading"]["temperature_c"] > 37.5
    assert data["analysis"]["overall_status"] in ("ATTENTION", "REVIEW")


def test_api_vitals_scenario_low_spo2_is_abnormal(client):
    response = client.get("/api/vitals?scenario=low_spo2&lang=en")
    data = response.get_json()
    assert data["scenario"] == "low_spo2"
    assert data["reading"]["spo2_percent"] < 95
    assert data["analysis"]["overall_status"] in ("ATTENTION", "REVIEW")


def test_api_vitals_scenario_critical_is_review(client):
    response = client.get("/api/vitals?scenario=critical&lang=en")
    data = response.get_json()
    assert data["scenario"] == "critical"
    assert data["analysis"]["overall_status"] == "REVIEW"


def test_api_vitals_invalid_scenario_falls_back_to_normal(client):
    response = client.get("/api/vitals?scenario=bogus")
    data = response.get_json()
    assert data["scenario"] == "normal"
    assert data["reading"]["simulated"] is True


def test_api_vitals_scenario_french_localized(client):
    response = client.get("/api/vitals?scenario=fever&lang=fr")
    data = response.get_json()
    assert data["analysis"]["overall_status_label"] in ("Attention", "À vérifier", "Normal")
    labels = {v["name"]: v["label"] for v in data["analysis"]["vitals"]}
    assert labels["heart_rate_bpm"] == "Fréquence cardiaque"


def test_api_vitals_scenario_normal_is_normal(client):
    data = client.get("/api/vitals?scenario=normal&lang=en").get_json()
    assert data["scenario"] == "normal"
    assert data["analysis"]["overall_status"] == "NORMAL"


def test_api_vitals_default_is_normal_monitoring(client):
    data = client.get("/api/vitals").get_json()
    assert data["scenario"] == "normal"
    assert data["analysis"]["overall_status"] == "NORMAL"


def test_api_vitals_scenario_tachycardia_is_attention(client):
    data = client.get("/api/vitals?scenario=tachycardia&lang=en").get_json()
    assert data["scenario"] == "tachycardia"
    assert data["analysis"]["overall_status"] == "ATTENTION"


def test_api_vitals_scenario_echoes_code(client):
    data = client.get("/api/vitals?scenario=low_spo2").get_json()
    assert data["scenario"] == "low_spo2"
    assert isinstance(data["analysis"]["vitals"][0]["low"], (int, float))
    assert isinstance(data["analysis"]["vitals"][0]["high"], (int, float))
