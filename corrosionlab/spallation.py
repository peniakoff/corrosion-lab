"""Spallation and anomaly detection via mass-change derivative."""

from __future__ import annotations

import pandas as pd

from corrosionlab.constants import TIME_COLUMN


def detect_spallation(
    df: pd.DataFrame,
    sample_columns: list[str],
) -> pd.DataFrame:
    """
    Flag cycles where mass decreases relative to the previous cycle.

    A negative mass increment indicates potential scale spallation.
    """
    alerts: list[dict[str, object]] = []

    for col in sample_columns:
        masses = df[col]
        times = df[TIME_COLUMN]
        delta = masses.diff()

        for idx in range(1, len(df)):
            dm = delta.iloc[idx]
            if pd.notna(dm) and dm < 0:
                alerts.append(
                    {
                        "sample": col,
                        "time_h": float(times.iloc[idx]),
                        "previous_time_h": float(times.iloc[idx - 1]),
                        "mass_before_g": float(masses.iloc[idx - 1]),
                        "mass_after_g": float(masses.iloc[idx]),
                        "mass_change_g": float(dm),
                        "severity": _severity(dm, masses.iloc[idx - 1]),
                    }
                )

    if not alerts:
        return pd.DataFrame(
            columns=[
                "sample",
                "time_h",
                "previous_time_h",
                "mass_before_g",
                "mass_after_g",
                "mass_change_g",
                "severity",
            ]
        )
    return pd.DataFrame(alerts)


def detect_spallation_all(
    df: pd.DataFrame,
    sample_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Detect spallation for all sample columns except time."""
    columns = sample_columns or [c for c in df.columns if c != TIME_COLUMN]
    return detect_spallation(df, columns)


def _severity(delta_mass: float, reference_mass: float) -> str:
    ratio = abs(delta_mass) / reference_mass
    if ratio >= 0.005:
        return "high"
    if ratio >= 0.001:
        return "medium"
    return "low"
