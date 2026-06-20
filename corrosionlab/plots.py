"""Plotly visualizations for oxidation kinetics analysis."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from corrosionlab.constants import TIME_COLUMN
from corrosionlab.fitting import FitResult

PLOT_TEMPLATE = "plotly_white"


def plot_mass_change(
    mass_change_pct: pd.DataFrame,
    samples: list[str] | None = None,
    title: str = "Względna zmiana masy Δm/m₀",
) -> go.Figure:
    """Plot relative mass change curves."""
    columns = samples or [c for c in mass_change_pct.columns if c != TIME_COLUMN]
    fig = go.Figure()
    for col in columns:
        fig.add_trace(
            go.Scatter(
                x=mass_change_pct[TIME_COLUMN],
                y=mass_change_pct[col],
                mode="lines+markers",
                name=col,
            )
        )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=title,
        xaxis_title="Czas utleniania [h]",
        yaxis_title="Δm/m₀ [%]",
        legend_title="Próbka",
        hovermode="x unified",
    )
    return fig


def plot_protective_effectiveness(
    sk_pct: pd.DataFrame,
    samples: list[str] | None = None,
    title: str = "Skuteczność ochronna S_k",
) -> go.Figure:
    """Plot protective effectiveness over time."""
    columns = samples or [c for c in sk_pct.columns if c != TIME_COLUMN]
    fig = go.Figure()
    for col in columns:
        fig.add_trace(
            go.Scatter(
                x=sk_pct[TIME_COLUMN],
                y=sk_pct[col],
                mode="lines+markers",
                name=col,
            )
        )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=title,
        xaxis_title="Czas utleniania [h]",
        yaxis_title="S_k [%]",
        legend_title="Próbka",
        hovermode="x unified",
    )
    return fig


def plot_spallation(
    mass_change_pct: pd.DataFrame,
    alerts: pd.DataFrame,
    samples: list[str] | None = None,
    title: str = "Detekcja odprysków zgorzeliny",
) -> go.Figure:
    """Plot mass-change curves with spallation alert markers."""
    fig = plot_mass_change(mass_change_pct, samples, title=title)

    if alerts.empty:
        return fig

    for _, row in alerts.iterrows():
        sample = str(row["sample"])
        time_h = float(row["time_h"])
        sample_rows = mass_change_pct[mass_change_pct[TIME_COLUMN] == time_h]
        if sample not in sample_rows.columns or sample_rows.empty:
            continue
        y_val = float(sample_rows[sample].iloc[0])
        fig.add_trace(
            go.Scatter(
                x=[time_h],
                y=[y_val],
                mode="markers",
                name=f"Odprysk {sample} @ {time_h:.0f}h",
                marker=dict(size=14, symbol="x", color="crimson"),
                showlegend=True,
            )
        )
    return fig


def plot_fit_extrapolation(
    fit_result: FitResult,
    sample_name: str,
    title: str | None = None,
) -> go.Figure:
    """Plot empirical data, fitted curve, confidence band, and extrapolation."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=fit_result.time_h,
            y=fit_result.observed,
            mode="markers",
            name="Dane empiryczne",
            marker=dict(size=8),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fit_result.fit_grid_time_h,
            y=fit_result.fit_grid_values,
            mode="lines",
            name=f"Dopasowanie ({fit_result.model})",
            line=dict(width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fit_result.fit_grid_time_h,
            y=fit_result.fit_grid_ci_upper,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=fit_result.fit_grid_time_h,
            y=fit_result.fit_grid_ci_lower,
            mode="lines",
            fill="tonexty",
            name="Przedział ufności 95%",
            line=dict(width=0),
            fillcolor="rgba(31, 78, 121, 0.15)",
        )
    )

    if len(fit_result.extrapolation_time_h):
        fig.add_trace(
            go.Scatter(
                x=fit_result.extrapolation_time_h,
                y=fit_result.extrapolation,
                mode="lines+markers",
                name="Ekstrapolacja",
                line=dict(dash="dash", color="darkorange"),
            )
        )

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=title or f"Ekstrapolacja kinetyki — {sample_name} (R²={fit_result.r_squared:.3f})",
        xaxis_title="Czas utleniania [h]",
        yaxis_title="Δm/m₀ [%]",
        hovermode="x unified",
    )
    return fig
