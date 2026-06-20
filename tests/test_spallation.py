"""Tests for spallation detection."""

from corrosionlab.io import load_default_data
from corrosionlab.spallation import detect_spallation_all


def test_tm4b_spallation_at_96h():
    df = load_default_data()
    alerts = detect_spallation_all(df)
    tm4b = alerts[alerts["sample"] == "TM4B"]
    assert not tm4b.empty
    assert 96.0 in tm4b["time_h"].values


def test_tm5a_spallation_at_96h():
    df = load_default_data()
    alerts = detect_spallation_all(df)
    tm5a = alerts[alerts["sample"] == "TM5A"]
    assert not tm5a.empty
    assert 96.0 in tm5a["time_h"].values


def test_spallation_negative_mass_increment():
    df = load_default_data()
    alerts = detect_spallation_all(df)
    assert (alerts["mass_change_g"] < 0).all()
