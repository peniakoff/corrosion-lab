"""Tests for curve fitting module."""

import numpy as np
import pytest

from corrosionlab.fitting import fit_kinetic_model


def test_parabolic_fit_r_squared():
    t = np.array([0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120], dtype=float)
    y = 0.05 * np.sqrt(t)
    result = fit_kinetic_model(t, y, model="parabolic", extrapolation_hours=[144, 168])
    assert result.r_squared > 0.99
    assert len(result.extrapolation_time_h) == 2


def test_linear_fit_requires_points():
    with pytest.raises(ValueError):
        fit_kinetic_model(np.array([0.0]), np.array([0.0]), model="linear")
