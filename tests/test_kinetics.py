"""Validation tests against thesis Table 9.3–9.4."""

import pytest

from corrosionlab.constants import THESIS_REFERENCE
from corrosionlab.io import load_default_data
from corrosionlab.kinetics import AnalysisConfig, analyze_all, value_at_time


@pytest.fixture
def analysis():
    df = load_default_data()
    return analyze_all(df, AnalysisConfig())


def test_control_mass_change_at_120h(analysis):
    expected = THESIS_REFERENCE["TM_Control"]["delta_m_pct_120h"]
    actual = value_at_time(analysis.mass_change_pct, "TM_Control", 120.0)
    assert actual == pytest.approx(expected, abs=0.5)


def test_tm4b_mass_change_at_120h(analysis):
    expected = THESIS_REFERENCE["TM4B"]["delta_m_pct_120h"]
    actual = value_at_time(analysis.mass_change_pct, "TM4B", 120.0)
    assert actual == pytest.approx(expected, abs=0.5)


def test_tm5a_mass_change_at_120h(analysis):
    expected = THESIS_REFERENCE["TM5A"]["delta_m_pct_120h"]
    actual = value_at_time(analysis.mass_change_pct, "TM5A", 120.0)
    assert actual == pytest.approx(expected, abs=0.5)


def test_tm4b_protective_effectiveness_at_120h(analysis):
    expected = THESIS_REFERENCE["TM4B"]["sk_120h"]
    actual = value_at_time(analysis.protective_effectiveness_pct, "TM4B", 120.0)
    assert actual == pytest.approx(expected, abs=0.5)


def test_tm5a_protective_effectiveness_at_120h(analysis):
    expected = THESIS_REFERENCE["TM5A"]["sk_120h"]
    actual = value_at_time(analysis.protective_effectiveness_pct, "TM5A", 120.0)
    assert actual == pytest.approx(expected, abs=0.5)


def test_tm1a_mass_change_at_120h(analysis):
    expected = THESIS_REFERENCE["TM1A"]["delta_m_pct_120h"]
    actual = value_at_time(analysis.mass_change_pct, "TM1A", 120.0)
    assert actual == pytest.approx(expected, abs=0.5)


def test_scale_thickness_nan_on_mass_loss(analysis):
    """Mass loss cycles should not produce scale thickness (Table 9.5 footnote)."""
    row = analysis.scale_thickness_um.loc[analysis.scale_thickness_um["time_h"] == 12.0]
    assert row["TM4B"].isna().iloc[0]


def test_parabolic_rate_zero_at_t0(analysis):
    row = analysis.parabolic_rate.loc[analysis.parabolic_rate["time_h"] == 0.0]
    assert row["TM_Control"].isna().iloc[0]


def test_sample_areas_positive(analysis):
    assert all(area > 0 for area in analysis.sample_areas_cm2.values())
