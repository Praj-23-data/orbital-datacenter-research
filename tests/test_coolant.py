"""Tests for coolant properties and pumping model."""
from __future__ import annotations

import pytest

from simulations.coolant import (
    COOLANTS,
    coolant_ranking_table,
    darcy_friction_factor,
    pumping_power,
    reynolds_number,
)


def test_all_coolants_have_positive_properties():
    for c in COOLANTS.values():
        assert c.cp_j_kg_k > 0
        assert c.density_kg_m3 > 0
        assert c.thermal_conductivity_w_m_k > 0
        assert c.boiling_point_k > c.melting_point_k


def test_liquid_range_positive():
    for c in COOLANTS.values():
        assert c.liquid_range_k > 0


def test_reynolds_increases_with_flow():
    re1 = reynolds_number(1.0, 0.02, 1e-3)
    re2 = reynolds_number(2.0, 0.02, 1e-3)
    assert re2 == pytest.approx(2 * re1, rel=1e-9)


def test_friction_factor_laminar_branch():
    assert darcy_friction_factor(1000.0) == pytest.approx(64.0 / 1000.0)


def test_pumping_fraction_is_small_and_physical():
    # A well-posed 100 MW loop should have parasitic pumping well under 1.
    for c in COOLANTS.values():
        pp = pumping_power(c, 100e6, 20.0)
        assert 0 < pp["pumping_fraction_of_load"] < 1.0
        assert pp["n_channels"] >= 1
        assert pp["velocity_m_s"] > 0


def test_ranking_table_sorted_by_pumping_fraction():
    df = coolant_ranking_table(100e6, 20.0)
    fracs = df["Pumping fraction"].tolist()
    assert fracs == sorted(fracs)
