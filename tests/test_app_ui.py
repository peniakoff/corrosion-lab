"""Streamlit UI smoke tests via AppTest."""

from io import BytesIO
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"
TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "data" / "template.csv"


@pytest.fixture
def app() -> AppTest:
    at = AppTest.from_file(str(APP_PATH))
    at.run(timeout=60)
    assert not at.exception, f"App crashed: {at.exception}"
    return at


def test_app_loads_with_title(app: AppTest):
    assert any("CorrosionLab" in t.value for t in app.title)


def test_demo_data_info_in_sidebar(app: AppTest):
    infos = [i.value for i in app.info]
    assert any("demo" in v.lower() or "tabela 9.1" in v.lower() for v in infos)


def test_all_tabs_present(app: AppTest):
    labels = [t.label for t in app.tabs]
    assert labels == [
        "Dashboard",
        "Analiza kinetyczna",
        "Spallation Alert",
        "Ekstrapolacja",
        "Doradca powłok",
    ]


def test_dashboard_sections(app: AppTest):
    subheaders = [s.value for s in app.subheader]
    assert "Teoria i dane wejściowe" in subheaders
    assert "Podgląd danych" in subheaders
    assert len(app.dataframe) >= 1


def test_analysis_tab_tables(app: AppTest):
    markdown = " ".join(m.value for m in app.markdown)
    assert "Tabela 9.3" in markdown
    assert "Tabela 9.4" in markdown
    assert "Tabela 9.5" in markdown
    assert "Tabela 9.6" in markdown
    assert len(app.dataframe) >= 4


def test_analysis_export_section(app: AppTest):
    subheaders = [s.value for s in app.subheader]
    assert "Eksport wyników" in subheaders


def test_spallation_tab_shows_alerts(app: AppTest):
    subheaders = [s.value for s in app.subheader]
    assert "Detektor odprysków zgorzeliny" in subheaders
    warnings = [w.value for w in app.warning]
    assert any("odprysk" in w.lower() for w in warnings)
    assert len(app.dataframe) >= 1


def test_extrapolation_tab_controls(app: AppTest):
    subheaders = [s.value for s in app.subheader]
    assert "Symulator i ekstrapolacja" in subheaders
    assert len(app.selectbox) >= 1
    assert len(app.slider) >= 1
    metric_labels = [m.label for m in app.metric]
    assert "R² dopasowania" in metric_labels


def test_expert_tab_recommendation(app: AppTest):
    subheaders = [s.value for s in app.subheader]
    assert "System ekspercki — doradca powłok" in subheaders
    assert len(app.success) >= 1
    metric_labels = [m.label for m in app.metric]
    assert "Kod próbki" in metric_labels
    assert "Oczekiwane Sₖ" in metric_labels


def test_csv_upload_with_template():
    at = AppTest.from_file(str(APP_PATH))
    at.run(timeout=60)
    assert not at.exception

    upload = at.sidebar.file_uploader[0]
    upload.upload("upload_test.csv", TEMPLATE_PATH.read_bytes(), mime_type="text/csv")
    at.run(timeout=60)
    assert not at.exception
    assert len(at.dataframe) >= 1


def test_expert_priority_change():
    at = AppTest.from_file(str(APP_PATH))
    at.run(timeout=60)
    assert not at.exception
    at.radio[0].set_value("max_protection").run(timeout=60)
    assert not at.exception
    success_text = " ".join(s.value for s in at.success)
    assert "ZrO" in success_text or "ochrona" in success_text.lower()

    at.radio[0].set_value("low_cost").run(timeout=60)
    assert not at.exception
    success_text = " ".join(s.value for s in at.success)
    assert "TM2A" in success_text or "Aerosil" in success_text or "cena" in success_text.lower()
