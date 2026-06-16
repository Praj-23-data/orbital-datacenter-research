"""Tests for semiconductor co-design models (the central hypothesis)."""
from __future__ import annotations

import numpy as np
import pytest

from simulations.semiconductors import (
    SEMICONDUCTORS,
    ThermalBudget,
    junction_temperature_sweep,
    material_comparison_table,
    radiator_temperature_from_junction,
)


def test_database_has_five_materials():
    assert {"silicon", "sic", "gan", "diamond", "ga2o3"} <= set(SEMICONDUCTORS)


def test_radiator_temp_below_junction():
    t = radiator_temperature_from_junction(600.0, ThermalBudget())
    assert t < 600.0
    assert t == pytest.approx(600.0 - ThermalBudget().total_k)


def test_budget_exceeding_junction_raises():
    with pytest.raises(ValueError):
        radiator_temperature_from_junction(40.0, ThermalBudget(50, 50, 50))


def test_higher_junction_temp_reduces_area_and_mass():
    df = junction_temperature_sweep(100e6, np.array([400.0, 800.0]))
    assert df["radiator_area_m2"].iloc[1] < df["radiator_area_m2"].iloc[0]
    assert df["radiator_mass_kg"].iloc[1] < df["radiator_mass_kg"].iloc[0]


def test_temperature_beats_emissivity():
    # Central thesis: doubling radiator T (T^4 -> 16x) dwarfs the <=2x from
    # any emissivity improvement.
    df = junction_temperature_sweep(
        100e6, np.array([400.0, 800.0]),
        budget=ThermalBudget(0, 0, 0),  # isolate the T effect
    )
    area_ratio = df["radiator_area_m2"].iloc[0] / df["radiator_area_m2"].iloc[1]
    assert area_ratio > 8.0  # far exceeds the 2x emissivity ceiling


def test_material_table_silicon_is_heaviest():
    df = material_comparison_table(100e6)
    si_mass = df.loc[df["Material"].str.startswith("Silicon (Si)"),
                     "Radiator mass [kg]"].values[0]
    assert si_mass == df["Radiator mass [kg]"].max()
