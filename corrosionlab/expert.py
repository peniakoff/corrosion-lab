"""Rule-based coating recommender from thesis conclusions A–I."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from corrosionlab.constants import SAMPLE_METADATA
from corrosionlab.i18n import Locale, get_message, t

Priority = Literal[
    "max_protection",
    "min_spallation",
    "low_cost",
    "multi_layer",
    "balanced",
]
LayerPreference = Literal["flexible", "single", "five"]
Budget = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class Recommendation:
    """Expert system output."""

    sample_code: str
    title: str
    description: str
    expected_sk_pct: str
    layers: int
    nanoparticle: str
    rules_applied: tuple[str, ...]


@dataclass(frozen=True)
class UserPreferences:
    """User inputs for the expert advisor."""

    priority: Priority = "balanced"
    layer_preference: LayerPreference = "flexible"
    budget: Budget = "medium"
    avoid_spallation: bool = True


def recommend_coating(
    preferences: UserPreferences,
    *,
    locale: Locale | None = None,
) -> Recommendation:
    """Return a coating recommendation based on IF-THEN rules from thesis conclusions."""
    if preferences.priority == "max_protection":
        return _build("TM4B", "max_protection", [], locale)

    if preferences.priority == "min_spallation":
        return _build("TM4B", "min_spallation", [], locale)

    if preferences.priority == "low_cost" or preferences.budget == "low":
        return _build("TM2A", "low_cost", [], locale)

    if preferences.layer_preference == "five" or preferences.priority == "multi_layer":
        return _build("TM4B", "multi_layer", [], locale)

    if preferences.layer_preference == "single":
        return _build("TM2A", "single_layer", [], locale)

    return _build("TM7B", "balanced", [], locale)


def list_all_recommendations(*, locale: Locale | None = None) -> list[Recommendation]:
    """Return baseline recommendations for each priority preset."""
    presets = [
        UserPreferences(priority="max_protection"),
        UserPreferences(priority="min_spallation"),
        UserPreferences(priority="low_cost"),
        UserPreferences(priority="multi_layer"),
        UserPreferences(priority="balanced"),
    ]
    return [recommend_coating(p, locale=locale) for p in presets]


def _build(
    sample_code: str,
    rec_key: str,
    rules: list[str],
    locale: Locale | None,
) -> Recommendation:
    prefix = f"expert.rec.{rec_key}"
    title = t(f"{prefix}.title", locale=locale)
    description = t(f"{prefix}.description", locale=locale)
    catalog_rules = get_message(f"{prefix}.rules", locale=locale)
    if isinstance(catalog_rules, list):
        rules = list(catalog_rules)

    meta = SAMPLE_METADATA[sample_code]
    sk = meta.sk_at_120h
    sk_range = f"~{sk:.0f}%" if sk is not None else t("expert.no_data", locale=locale)
    if sample_code == "TM4B":
        sk_range = "80–100%"

    return Recommendation(
        sample_code=sample_code,
        title=title,
        description=description,
        expected_sk_pct=sk_range,
        layers=meta.layers,
        nanoparticle=meta.nanoparticle,
        rules_applied=tuple(rules),
    )
