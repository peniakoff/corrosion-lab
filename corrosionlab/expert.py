"""Rule-based coating recommender from thesis conclusions A–I."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from corrosionlab.constants import SAMPLE_METADATA

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


def recommend_coating(preferences: UserPreferences) -> Recommendation:
    """Return a coating recommendation based on IF-THEN rules from thesis conclusions."""
    rules: list[str] = []

    if preferences.priority == "max_protection":
        rules.append("C: SiO₂ matrix with ZrO₂ nanoparticles shows highest protective effectiveness.")
        return _build(
            "TM4B",
            "Maksymalna ochrona — ZrO₂ (5 warstw)",
            "Pięciowarstwowa powłoka z nanocząstkami ZrO₂ stabilizowanymi itrem "
            "wykazała skuteczność ochronną ~100% (wniosek C, próbka TM4B).",
            rules,
        )

    if preferences.priority == "min_spallation":
        rules.append("F: Y₂O₃ increases spallation risk; ZrO₂ improves high-temperature resistance.")
        rules.append("D: Five-layer coatings generally outperform single-layer variants.")
        return _build(
            "TM4B",
            "Minimalny odprysk — unikaj Y₂O₃, preferuj ZrO₂",
            "Powłoki z Y₂O₃ (TM5A/TM5B) wykazują odpryski i niższą skuteczność. "
            "ZrO₂ w matrycy SiO₂ (5 warstw) daje najlepszą stabilność zgorzeliny.",
            rules,
        )

    if preferences.priority == "low_cost" or preferences.budget == "low":
        rules.append("B: Sol-gel coatings are easy to apply without costly equipment.")
        rules.append("D: Single-layer coatings are cheaper but less effective.")
        return _build(
            "TM2A",
            "Niska cena — pojedyncza warstwa SiO₂ (Aerosil 380)",
            "Jednowarstwowa powłoka SiO₂ z Aerosil 380 (TM2A) zapewnia ~55% skuteczności "
            "przy prostszej aplikacji i niższych kosztach.",
            rules,
        )

    if preferences.layer_preference == "five" or preferences.priority == "multi_layer":
        rules.append("D: Five-layer coatings provide better protection than single-layer SiO₂.")
        rules.append("H: Reactive metal oxide nanoparticles reach 27–100% effectiveness.")
        return _build(
            "TM4B",
            "Wielowarstwowa ochrona — 5 warstw ZrO₂",
            "Reguła D: pięciowarstwowe powłoki zapewniają lepszą ochronę. "
            "TM4B (ZrO₂, 5 warstw) — skuteczność ~80–100%.",
            rules,
        )

    if preferences.layer_preference == "single":
        rules.append("H: Single-layer reactive oxides still outperform Al₂O₃/SiO₂ fillers.")
        return _build(
            "TM2A",
            "Pojedyncza warstwa — SiO₂ Aerosil 380",
            "Kompromis między kosztem a skutecznością: TM2A (~55% S_k).",
            rules,
        )

    # Balanced default — CeO₂/ZrO₂ composite as middle ground
    rules.append("G: Nanoparticle type affects scale morphology and oxidation rate.")
    rules.append("H: Reactive metal oxides (CeO₂/ZrO₂) reach moderate-to-high effectiveness.")
    return _build(
        "TM7B",
        "Zbalansowana rekomendacja — CeO₂/ZrO₂ (5 warstw)",
        "Powłoka TM7B (CeO₂/ZrO₂, 5 warstw) łączy umiarkowaną skuteczność (~40%) "
        "z dobrą morfologią zgorzeliny — kompromis między kosztem a ochroną.",
        rules,
    )


def list_all_recommendations() -> list[Recommendation]:
    """Return baseline recommendations for each priority preset."""
    presets = [
        UserPreferences(priority="max_protection"),
        UserPreferences(priority="min_spallation"),
        UserPreferences(priority="low_cost"),
        UserPreferences(priority="multi_layer"),
        UserPreferences(priority="balanced"),
    ]
    return [recommend_coating(p) for p in presets]


def _build(
    sample_code: str,
    title: str,
    description: str,
    rules: list[str],
) -> Recommendation:
    meta = SAMPLE_METADATA[sample_code]
    sk = meta.sk_at_120h
    sk_range = f"~{sk:.0f}%" if sk is not None else "brak danych"
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
