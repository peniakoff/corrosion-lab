"""Tests for the rule-based coating recommender."""

from corrosionlab.expert import UserPreferences, recommend_coating


def test_max_protection_recommends_tm4b():
    rec = recommend_coating(UserPreferences(priority="max_protection"))
    assert rec.sample_code == "TM4B"
    assert rec.layers == 5


def test_min_spallation_avoids_yttria():
    rec = recommend_coating(UserPreferences(priority="min_spallation"))
    assert rec.sample_code == "TM4B"
    assert "Y₂O₃" in rec.description or "Y" in rec.description


def test_low_cost_recommends_single_layer():
    rec = recommend_coating(UserPreferences(priority="low_cost"))
    assert rec.sample_code == "TM2A"
    assert rec.layers == 1


def test_multi_layer_prefers_five_layers():
    rec = recommend_coating(UserPreferences(priority="multi_layer"))
    assert rec.sample_code == "TM4B"
    assert rec.layers == 5


def test_balanced_recommendation():
    rec = recommend_coating(UserPreferences(priority="balanced"))
    assert rec.sample_code == "TM7B"
    assert rec.rules_applied
