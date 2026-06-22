"""Plotly visualizations for oxidation kinetics analysis."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from corrosionlab.constants import TIME_COLUMN
from corrosionlab.fitting import FitResult
from corrosionlab.i18n import Locale, get_locale, t

PLOT_TEMPLATE = "plotly_white"


def plot_mass_change(
    mass_change_pct: pd.DataFrame,
    samples: list[str] | None = None,
    title: str | None = None,
    *,
    locale: Locale | None = None,
) -> go.Figure:
    """Plot relative mass change curves."""
    active = locale or get_locale()
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
        title=title or t("plots.mass_change.title", locale=active),
        xaxis_title=t("plots.mass_change.xaxis", locale=active),
        yaxis_title=t("plots.mass_change.yaxis", locale=active),
        legend_title=t("plots.mass_change.legend", locale=active),
        hovermode="x unified",
    )
    return fig


def plot_protective_effectiveness(
    sk_pct: pd.DataFrame,
    samples: list[str] | None = None,
    title: str | None = None,
    *,
    locale: Locale | None = None,
) -> go.Figure:
    """Plot protective effectiveness over time."""
    active = locale or get_locale()
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
        title=title or t("plots.protective.title", locale=active),
        xaxis_title=t("plots.protective.xaxis", locale=active),
        yaxis_title=t("plots.protective.yaxis", locale=active),
        legend_title=t("plots.protective.legend", locale=active),
        hovermode="x unified",
    )
    return fig


def plot_spallation(
    mass_change_pct: pd.DataFrame,
    alerts: pd.DataFrame,
    samples: list[str] | None = None,
    title: str | None = None,
    *,
    locale: Locale | None = None,
) -> go.Figure:
    """Plot mass-change curves with spallation alert markers."""
    active = locale or get_locale()
    fig = plot_mass_change(
        mass_change_pct,
        samples,
        title=title or t("plots.spallation.title", locale=active),
        locale=active,
    )

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
                name=t(
                    "plots.spallation.marker",
                    locale=active,
                    sample=sample,
                    time=time_h,
                ),
                marker=dict(size=14, symbol="x", color="crimson"),
                showlegend=True,
            )
        )
    return fig


def plot_fit_extrapolation(
    fit_result: FitResult,
    sample_name: str,
    title: str | None = None,
    *,
    locale: Locale | None = None,
) -> go.Figure:
    """Plot empirical data, fitted curve, confidence band, and extrapolation."""
    active = locale or get_locale()
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=fit_result.time_h,
            y=fit_result.observed,
            mode="markers",
            name=t("plots.fit.empirical", locale=active),
            marker=dict(size=8),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fit_result.fit_grid_time_h,
            y=fit_result.fit_grid_values,
            mode="lines",
            name=t("plots.fit.fit_trace", locale=active, model=fit_result.model),
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
            name=t("plots.fit.ci_95", locale=active),
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
                name=t("plots.fit.extrapolation", locale=active),
                line=dict(dash="dash", color="darkorange"),
            )
        )

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=title
        or t(
            "plots.fit.title",
            locale=active,
            sample=sample_name,
            r2=fit_result.r_squared,
        ),
        xaxis_title=t("plots.fit.xaxis", locale=active),
        yaxis_title=t("plots.fit.yaxis", locale=active),
        hovermode="x unified",
    )
    return fig
