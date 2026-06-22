"""Streamlit UI smoke tests via AppTest."""

from io import BytesIO
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from corrosionlab.i18n import set_locale, t

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"
TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "data" / "template.csv"


def _run_app(locale: str) -> AppTest:
    set_locale(locale)
    at = AppTest.from_file(str(APP_PATH))
    at.session_state["locale"] = locale
    at.run(timeout=60)
    assert not at.exception, f"App crashed: {at.exception}"
    return at


@pytest.fixture(params=["pl", "en"])
def app(request) -> AppTest:
    return _run_app(request.param)


@pytest.fixture
def app_pl() -> AppTest:
    return _run_app("pl")


@pytest.fixture
def app_en() -> AppTest:
    return _run_app("en")


def test_app_loads_with_title(app: AppTest):
    assert any("CorrosionLab" in title.value for title in app.title)


def test_demo_data_info_in_sidebar(app: AppTest):
    infos = [info.value for info in app.info]
    locale = app.session_state["locale"]
    demo_text = t("sidebar.demo_data", locale=locale).lower()
    assert any(demo_text in info.lower() or "demo" in info.lower() for info in infos)


def test_all_tabs_present(app: AppTest):
    locale = app.session_state["locale"]
    expected = [
        t("tabs.dashboard", locale=locale),
        t("tabs.kinetics", locale=locale),
        t("tabs.spallation", locale=locale),
        t("tabs.extrapolation", locale=locale),
        t("tabs.expert", locale=locale),
    ]
    labels = [tab.label for tab in app.tabs]
    assert labels == expected


def test_dashboard_sections(app: AppTest):
    locale = app.session_state["locale"]
    subheaders = [subheader.value for subheader in app.subheader]
    assert t("dashboard.theory_header", locale=locale) in subheaders
    assert t("dashboard.data_preview", locale=locale) in subheaders
    assert len(app.dataframe) >= 1


def test_analysis_tab_tables(app: AppTest):
    markdown = " ".join(block.value for block in app.markdown)
    assert "Tabela 9.3" in markdown or "Table 9.3" in markdown
    assert "Tabela 9.4" in markdown or "Table 9.4" in markdown
    assert "Tabela 9.5" in markdown or "Table 9.5" in markdown
    assert "Tabela 9.6" in markdown or "Table 9.6" in markdown
    assert len(app.dataframe) >= 4


def test_analysis_export_section(app: AppTest):
    locale = app.session_state["locale"]
    subheaders = [subheader.value for subheader in app.subheader]
    assert t("analysis.export_header", locale=locale) in subheaders


def test_spallation_tab_shows_alerts(app: AppTest):
    locale = app.session_state["locale"]
    subheaders = [subheader.value for subheader in app.subheader]
    assert t("spallation.header", locale=locale) in subheaders
    assert len(app.warning) >= 1 or len(app.success) >= 1
    assert len(app.dataframe) >= 1


def test_extrapolation_tab_controls(app: AppTest):
    locale = app.session_state["locale"]
    subheaders = [subheader.value for subheader in app.subheader]
    assert t("extrapolation.header", locale=locale) in subheaders
    assert len(app.selectbox) >= 1
    assert len(app.slider) >= 1
    metric_labels = [metric.label for metric in app.metric]
    assert t("extrapolation.r_squared", locale=locale) in metric_labels


def test_expert_tab_recommendation(app: AppTest):
    locale = app.session_state["locale"]
    subheaders = [subheader.value for subheader in app.subheader]
    assert t("expert.header", locale=locale) in subheaders
    assert len(app.success) >= 1
    metric_labels = [metric.label for metric in app.metric]
    assert t("expert.sample_code", locale=locale) in metric_labels
    assert t("expert.expected_sk", locale=locale) in metric_labels


def test_csv_upload_with_template():
    at = _run_app("pl")
    upload = at.sidebar.file_uploader[0]
    upload.upload("upload_test.csv", TEMPLATE_PATH.read_bytes(), mime_type="text/csv")
    at.run(timeout=60)
    assert not at.exception
    assert len(at.dataframe) >= 1


def test_expert_priority_change():
    at = _run_app("pl")
    at.radio[0].set_value("max_protection").run(timeout=60)
    assert not at.exception
    success_text = " ".join(success.value for success in at.success)
    assert "TM4B" in success_text or "ZrO" in success_text

    at.radio[0].set_value("low_cost").run(timeout=60)
    assert not at.exception
    success_text = " ".join(success.value for success in at.success)
    assert "TM2A" in success_text or "Aerosil" in success_text
