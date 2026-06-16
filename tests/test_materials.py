"""Tests for structural materials, coatings and fin efficiency."""
from __future__ import annotations

import pytest

from simulations.materials import (
    COATINGS,
    STRUCTURAL_MATERIALS,
    fin_efficiency,
)


def test_structural_materials_positive():
    for m in STRUCTURAL_MATERIALS.values():
        assert m.density_kg_m3 > 0
        assert m.thermal_conductivity_w_m_k > 0
        assert m.representative_areal_density_kg_m2 > 0


def test_coating_alpha_over_epsilon():
    osr = COATINGS["osr"]
    assert osr.alpha_over_epsilon == pytest.approx(
        osr.solar_absorptance / osr.ir_emittance
    )
    # A good radiator coating has alpha/epsilon well below 1.
    assert osr.alpha_over_epsilon < 0.2


def test_fin_efficiency_between_zero_and_one():
    eta = fin_efficiency(0.1, 0.002, 167.0, 0.85, 350.0)
    assert 0.0 < eta <= 1.0


def test_fin_efficiency_drops_for_longer_fin():
    short = fin_efficiency(0.05, 0.002, 167.0, 0.85, 350.0)
    long = fin_efficiency(0.5, 0.002, 167.0, 0.85, 350.0)
    assert long < short
