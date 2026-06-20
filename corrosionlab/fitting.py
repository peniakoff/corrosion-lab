"""Predictive curve fitting and extrapolation with confidence intervals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

ModelType = Literal["linear", "parabolic", "paralinear"]


@dataclass
class FitResult:
    """Non-linear regression output for a kinetic model."""

    model: ModelType
    params: np.ndarray
    param_errors: np.ndarray
    r_squared: float
    time_h: np.ndarray
    observed: np.ndarray
    fitted: np.ndarray
    extrapolation_time_h: np.ndarray
    extrapolation: np.ndarray
    fit_grid_time_h: np.ndarray
    fit_grid_values: np.ndarray
    fit_grid_ci_lower: np.ndarray
    fit_grid_ci_upper: np.ndarray


def _linear_model(t: np.ndarray, a: float) -> np.ndarray:
    return a * t


def _parabolic_model(t: np.ndarray, a: float) -> np.ndarray:
    return a * np.sqrt(np.maximum(t, 0.0))


def _paralinear_model(t: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * np.sqrt(np.maximum(t, 0.0)) + b * t


def _model_spec(model: ModelType) -> tuple:
    if model == "linear":
        return _linear_model, [1.0]
    if model == "parabolic":
        return _parabolic_model, [0.1]
    if model == "paralinear":
        return _paralinear_model, [0.1, 0.01]
    raise ValueError(f"Nieobsługiwany model: {model}")


def _predict(model: ModelType, t: np.ndarray, params: np.ndarray) -> np.ndarray:
    func, _ = _model_spec(model)
    return func(t, *params)


def _r_squared(y: np.ndarray, y_hat: np.ndarray) -> float:
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    if ss_tot == 0:
        return 1.0
    return float(1.0 - ss_res / ss_tot)


def fit_kinetic_model(
    time_h: np.ndarray | pd.Series,
    delta_m_pct: np.ndarray | pd.Series,
    model: ModelType = "parabolic",
    extrapolation_hours: list[int] | None = None,
    confidence: float = 0.95,
) -> FitResult:
    """Fit a kinetic model and extrapolate beyond measured data."""
    t = np.asarray(time_h, dtype=float)
    y = np.asarray(delta_m_pct, dtype=float)

    mask = np.isfinite(t) & np.isfinite(y) & (t >= 0)
    t = t[mask]
    y = y[mask]

    if len(t) < 2:
        raise ValueError("Potrzeba co najmniej dwóch punktów pomiarowych do dopasowania.")

    func, p0 = _model_spec(model)
    params, pcov = curve_fit(func, t, y, p0=p0, maxfev=10_000)
    param_errors = np.sqrt(np.diag(pcov)) if pcov.size else np.zeros_like(params)

    fitted = _predict(model, t, params)
    r2 = _r_squared(y, fitted)

    max_time = float(np.max(t))
    future = extrapolation_hours or [int(max_time + 24), int(max_time + 48)]
    future = sorted({int(h) for h in future if h > max_time})
    extrap_t = np.array(future, dtype=float) if future else np.array([], dtype=float)

    grid = np.linspace(0.0, max(extrap_t.max() if len(extrap_t) else max_time, max_time), 200)
    mean = _predict(model, grid, params)
    ci_lower, ci_upper = _confidence_band(model, grid, params, pcov, confidence)

    return FitResult(
        model=model,
        params=params,
        param_errors=param_errors,
        r_squared=r2,
        time_h=t,
        observed=y,
        fitted=fitted,
        extrapolation_time_h=extrap_t,
        extrapolation=_predict(model, extrap_t, params) if len(extrap_t) else np.array([]),
        fit_grid_time_h=grid,
        fit_grid_values=mean,
        fit_grid_ci_lower=ci_lower,
        fit_grid_ci_upper=ci_upper,
    )


def extrapolate(
    fit_result: FitResult,
    future_hours: list[int],
) -> pd.DataFrame:
    """Build a dataframe of extrapolated values."""
    t = np.array(future_hours, dtype=float)
    y = _predict(fit_result.model, t, fit_result.params)
    ci_lower, ci_upper = _confidence_band(
        fit_result.model,
        t,
        fit_result.params,
        None,
        0.95,
        fit_result.param_errors,
    )
    return pd.DataFrame(
        {
            "time_h": t,
            "predicted_delta_m_pct": y,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
        }
    )


def _confidence_band(
    model: ModelType,
    t: np.ndarray,
    params: np.ndarray,
    pcov: np.ndarray | None,
    confidence: float,
    param_errors: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Approximate confidence band using parameter standard errors."""
    from scipy.stats import t as t_dist

    if param_errors is None:
        if pcov is None or pcov.size == 0:
            pred = _predict(model, t, params)
            return pred, pred
        param_errors = np.sqrt(np.diag(pcov))

    # Simple delta-method style band: perturb each parameter independently
    z = t_dist.ppf(0.5 + confidence / 2.0, max(len(t) - len(params), 1))
    base = _predict(model, t, params)
    spread = np.zeros_like(base)

    for i, err in enumerate(param_errors):
        perturbed = params.copy()
        perturbed[i] += err
        spread += np.abs(_predict(model, t, perturbed) - base)

    margin = z * spread / max(len(params), 1)
    return base - margin, base + margin
