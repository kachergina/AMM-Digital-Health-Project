"""Tests for the AMM Digital System dashboard.

Run them from the digital_system/ folder with:  pytest
"""

EXPECTED_DISCLAIMER = "NOT A REAL MEDICAL DEVICE"


def test_dashboard_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_dashboard_contains_disclaimer(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert EXPECTED_DISCLAIMER in body
    assert "Run simulation" in body


def test_dashboard_shows_pipeline(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    for stage in ("Simulated sensors", "Data processing", "Flask API", "Dashboard"):
        assert stage in body
    assert "pipeline" in body


def test_dashboard_has_components_container(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "components-list" in body
    assert "Simulated AMM components" in body


def test_dashboard_default_language_is_english(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "Run simulation" in body
    assert "Body temperature" in body
    assert "data-lang=\"en\"" in body


def test_dashboard_french_localized(client):
    response = client.get("/?lang=fr")
    body = response.get_data(as_text=True)
    assert "Lancer la simulation" in body
    assert "Température corporelle" in body
    assert "data-lang=\"fr\"" in body
    assert "SIMULATION — DONNÉES SIMULÉES" in body


def test_dashboard_russian_localized(client):
    response = client.get("/?lang=ru")
    body = response.get_data(as_text=True)
    assert "Запустить симуляцию" in body
    assert "Температура тела" in body
    assert "data-lang=\"ru\"" in body
    assert "СИМУЛЯЦИЯ — СМОДЕЛИРОВАННЫЕ ДАННЫЕ" in body


def test_dashboard_invalid_lang_falls_back_to_english(client):
    response = client.get("/?lang=xx")
    body = response.get_data(as_text=True)
    assert "Run simulation" in body
    assert "data-lang=\"en\"" in body


def test_favicon_svg_served(client):
    response = client.get("/favicon.svg")
    assert response.status_code == 200
    assert "image" in response.content_type


def test_favicon_ico_served(client):
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert "image" in response.content_type


def test_dashboard_static_css_loads(client):
    response = client.get("/static/dashboard.css")
    assert response.status_code == 200
    assert "text" in response.content_type


def test_dashboard_static_js_loads(client):
    response = client.get("/static/dashboard.js")
    assert response.status_code == 200


def test_api_endpoints_still_work_with_dashboard(client):
    assert client.get("/api/vitals").status_code == 200
    assert client.get("/api/status").status_code == 200


def test_main_dashboard_has_no_scenario_select(client):
    body = client.get("/").get_data(as_text=True)
    assert "scenario-select" not in body


def test_dashboard_has_demo_mode_panel(client):
    body = client.get("/").get_data(as_text=True)
    assert 'id="demo-toggle"' in body
    assert 'id="demo-panel"' in body
    assert "Demo Mode" in body
    assert 'id="demo-exit"' in body


def test_dashboard_demo_mode_shows_five_scenarios_en(client):
    body = client.get("/").get_data(as_text=True)
    for key in ("normal", "fever", "low_spo2", "tachycardia", "critical"):
        assert 'data-scenario="%s"' % key in body
    assert ">Fever<" in body
    assert ">Critical<" in body


def test_dashboard_demo_mode_localized_fr(client):
    body = client.get("/?lang=fr").get_data(as_text=True)
    assert "Mode démo" in body
    assert ">Fièvre<" in body
    assert ">Faible oxygène sanguin<" in body


def test_dashboard_demo_mode_localized_ru(client):
    body = client.get("/?lang=ru").get_data(as_text=True)
    assert "Демо-режим" in body
    assert ">Тахикардия<" in body
    assert ">Критический<" in body


def test_dashboard_has_export_buttons(client):
    body = client.get("/").get_data(as_text=True)
    assert 'id="export-json"' in body
    assert 'id="export-csv"' in body
    assert "Download JSON" in body
    assert "Download CSV" in body


def test_dashboard_has_four_vital_charts(client):
    body = client.get("/").get_data(as_text=True)
    for chart_id in ("temp-chart", "heart-chart", "spo2-chart", "resp-chart"):
        assert 'id="%s"' % chart_id in body


def test_dashboard_chart_titles_localized(client):
    body = client.get("/?lang=fr").get_data(as_text=True)
    assert "Tendance de la température corporelle (simulée)" in body
    assert "Tendance de la fréquence respiratoire (simulée)" in body


def test_dashboard_has_events_log(client):
    body = client.get("/").get_data(as_text=True)
    assert 'id="events-list"' in body
    assert "Detections" in body


def test_dashboard_events_log_localized_fr(client):
    body = client.get("/?lang=fr").get_data(as_text=True)
    assert "Détections" in body


def test_dashboard_has_pipeline_detail_spans(client):
    body = client.get("/").get_data(as_text=True)
    for detail_id in ("detail-sensors", "detail-processing", "detail-api", "detail-dashboard"):
        assert 'id="%s"' % detail_id in body

