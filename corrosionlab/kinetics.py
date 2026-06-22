"""Kinetics and gravimetry calculations (equations 9.1–9.4)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from corrosionlab.constants import (
    DEFAULT_CONTROL_COLUMN,
    M_AL2O3,
    M_O,
    M_REF,
    RHO_AL2O3,
    S_REF,
    SECONDS_PER_HOUR,
    TIME_COLUMN,
)
from corrosionlab.i18n import LocalizedError


@dataclass
class AnalysisConfig:
    """Physical parameters for oxidation analysis."""

    control_column: str = DEFAULT_CONTROL_COLUMN
    m_al2o3: float = M_AL2O3
    m_o: float = M_O
    rho_al2o3: float = RHO_AL2O3
    m_ref: float = M_REF
    s_ref: float = S_REF
    sample_columns: list[str] | None = None


@dataclass
class AnalysisResult:
    """Complete analysis output for all samples."""

    mass_change_pct: pd.DataFrame
    protective_effectiveness_pct: pd.DataFrame
    scale_thickness_um: pd.DataFrame
    parabolic_rate: pd.DataFrame
    sample_areas_cm2: dict[str, float]
    config: AnalysisConfig


def sample_surface_area(m0: float, config: AnalysisConfig) -> float:
    """Compute sample surface area proportional to initial mass (thesis section 9)."""
    return config.s_ref * (m0 / config.m_ref)


def compute_sample_areas(df: pd.DataFrame, config: AnalysisConfig) -> dict[str, float]:
    """Return surface area [cm²] for each sample column."""
    t0 = df[df[TIME_COLUMN] == df[TIME_COLUMN].min()]
    if t0.empty:
        t0 = df.iloc[[0]]

    areas: dict[str, float] = {}
    columns = _resolve_sample_columns(df, config)
    for col in columns:
        m0 = float(t0[col].iloc[0])
        areas[col] = sample_surface_area(m0, config)
    return areas


def compute_mass_change(
    df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    """Equation 9.1 — relative mass change Δm/m₀ [%]."""
    columns = _resolve_sample_columns(df, config)
    t0 = df[df[TIME_COLUMN] == df[TIME_COLUMN].min()]
    if t0.empty:
        t0 = df.iloc[[0]]

    result = df[[TIME_COLUMN]].copy()
    for col in columns:
        m0 = float(t0[col].iloc[0])
        delta_m = df[col] - m0
        result[col] = (delta_m / m0) * 100.0
    return result


def compute_protective_effectiveness(
    df: pd.DataFrame,
    config: AnalysisConfig,
) -> pd.DataFrame:
    """Equation 9.2 — protective effectiveness S_k [%]."""
    if config.control_column not in df.columns:
        raise LocalizedError("missing_control_column", column=config.control_column)

    columns = _resolve_sample_columns(df, config)
    coated_columns = [c for c in columns if c != config.control_column]

    t0 = df[df[TIME_COLUMN] == df[TIME_COLUMN].min()]
    if t0.empty:
        t0 = df.iloc[[0]]

    m0_control = float(t0[config.control_column].iloc[0])
    delta_m_n = df[config.control_column] - m0_control

    result = df[[TIME_COLUMN]].copy()
    for col in coated_columns:
        m0 = float(t0[col].iloc[0])
        delta_m_c = df[col] - m0
        with np.errstate(divide="ignore", invalid="ignore"):
            sk = np.where(
                np.isclose(delta_m_n, 0.0),
                np.nan,
                ((delta_m_n - delta_m_c) / delta_m_n) * 100.0,
            )
        result[col] = sk
    return result


def compute_scale_thickness(
    df: pd.DataFrame,
    config: AnalysisConfig,
    areas: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Equation 9.3 — scale thickness h [μm]."""
    if areas is None:
        areas = compute_sample_areas(df, config)

    columns = _resolve_sample_columns(df, config)
    t0 = df[df[TIME_COLUMN] == df[TIME_COLUMN].min()]
    if t0.empty:
        t0 = df.iloc[[0]]

    factor = config.m_al2o3 / (3.0 * config.m_o)
    result = df[[TIME_COLUMN]].copy()

    for col in columns:
        m0 = float(t0[col].iloc[0])
        delta_m = df[col] - m0
        s = areas[col]
        with np.errstate(divide="ignore", invalid="ignore"):
            h_cm = factor * delta_m / (config.rho_al2o3 * s)
            h_um = h_cm * 10_000.0
        h_um = np.where(delta_m < 0, np.nan, h_um)
        result[col] = h_um
    return result


def compute_parabolic_rate(
    df: pd.DataFrame,
    config: AnalysisConfig,
    areas: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Equation 9.4 — parabolic rate constant k_p [g²·cm⁻⁴·s⁻¹]."""
    if areas is None:
        areas = compute_sample_areas(df, config)

    columns = _resolve_sample_columns(df, config)
    t0 = df[df[TIME_COLUMN] == df[TIME_COLUMN].min()]
    if t0.empty:
        t0 = df.iloc[[0]]

    result = df[[TIME_COLUMN]].copy()
    time_s = df[TIME_COLUMN] * SECONDS_PER_HOUR

    for col in columns:
        m0 = float(t0[col].iloc[0])
        delta_m = df[col] - m0
        s = areas[col]
        with np.errstate(divide="ignore", invalid="ignore"):
            kp = np.where(
                time_s <= 0,
                np.nan,
                np.square(delta_m / s) / time_s,
            )
        result[col] = kp
    return result


def analyze_all(df: pd.DataFrame, config: AnalysisConfig | None = None) -> AnalysisResult:
    """Run the full gravimetric analysis pipeline."""
    cfg = config or AnalysisConfig()
    areas = compute_sample_areas(df, cfg)
    return AnalysisResult(
        mass_change_pct=compute_mass_change(df, cfg),
        protective_effectiveness_pct=compute_protective_effectiveness(df, cfg),
        scale_thickness_um=compute_scale_thickness(df, cfg, areas),
        parabolic_rate=compute_parabolic_rate(df, cfg, areas),
        sample_areas_cm2=areas,
        config=cfg,
    )


def value_at_time(table: pd.DataFrame, sample: str, time_h: float) -> float:
    """Return a computed value for a sample at a given oxidation time."""
    row = table.loc[table[TIME_COLUMN] == time_h]
    if row.empty:
        raise LocalizedError("missing_time_data", time_h=time_h)
    return float(row[sample].iloc[0])


def _resolve_sample_columns(df: pd.DataFrame, config: AnalysisConfig) -> list[str]:
    if config.sample_columns:
        return list(config.sample_columns)
    return [col for col in df.columns if col != TIME_COLUMN]
