"""Tests for the i18n module."""

import json
from pathlib import Path

import pytest

from corrosionlab.i18n import (
    DEFAULT_LOCALE,
    _flatten_messages,
    _load_catalog,
    format_error,
    map_browser_locale_tag,
    set_locale,
    t,
)
from corrosionlab.io import DataValidationError

LOCALES_DIR = Path(__file__).resolve().parent.parent / "corrosionlab" / "locales"


def _all_keys(locale: str) -> set[str]:
    with (LOCALES_DIR / f"{locale}.json").open(encoding="utf-8") as handle:
        return set(_flatten_messages(json.load(handle)).keys())


def test_pl_and_en_catalogs_have_same_keys():
    pl_keys = _all_keys("pl")
    en_keys = _all_keys("en")
    assert pl_keys == en_keys


def test_t_interpolation():
    set_locale("en")
    message = t("analysis.report_alerts", count=3)
    assert "3" in message
    assert "Spallation" in message


def test_format_error():
    exc = DataValidationError("csv_empty")
    assert format_error(exc, locale="en") == "The CSV file is empty."
    assert format_error(exc, locale="pl") == "Plik CSV jest pusty."


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("en-US", "en"),
        ("en", "en"),
        ("pl-PL", "pl"),
        ("pl", "pl"),
        ("de-DE", "en"),
        (None, DEFAULT_LOCALE),
        ("", DEFAULT_LOCALE),
    ],
)
def test_map_browser_locale_tag(tag: str | None, expected: str):
    assert map_browser_locale_tag(tag) == expected


def test_tab_labels_exist_in_both_locales():
    for locale in ("pl", "en"):
        catalog = _load_catalog(locale)
        for key in (
            "tabs.dashboard",
            "tabs.kinetics",
            "tabs.spallation",
            "tabs.extrapolation",
            "tabs.expert",
        ):
            assert key in catalog
