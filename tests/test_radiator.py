"""Tests for the radiator physics and sizing models."""

from __future__ import annotations

import math

import numpy as np
import pytest

from simulations.constants import STEFAN_BOLTZMANN
from simulations.physics import radiated_power, radiator_area
from simulations.radiator import (
    metamaterial_emissivity_sweep,
    size_droplet_radiator,
    size_liquid_sheet_radiator,
    size_panel_radiator,
)


def test_stefan_boltzmann_known_value():
    # Net emission to the 2.725 K CMB sink that the function correctly includes.
    from simulations.constants import DEEP_SPACE_TEMPERATURE

    p = radiated_power(area=1.0, temperature=300.0, emissivity=1.0)
    expected = STEFAN_BOLTZMANN * (300.0**4 - DEEP_SPACE_TEMPERATURE**4)
    assert p == pytest.approx(expected, rel=1e-12)
    # The sink term is negligible at 300 K: result ~ 459.3 W.
    assert p == pytest.approx(459.3, rel=1e-3)


def test_radiated_power_scales_as_t4():
    p1 = radiated_power(1.0, 300.0, 1.0)
    p2 = radiated_power(1.0, 600.0, 1.0)
    # Doubling T raises power by 2^4 = 16 (sink term negligible).
    assert p2 / p1 == pytest.approx(16.0, rel=1e-3)


def test_area_inverts_power():
    q = 1e5
    t = 400.0
    a = radiator_area(q, t, emissivity=0.9, radiating_sides=1)
    # Feeding that area back should reproduce the heat load.
    assert radiated_power(a, t, 0.9) == pytest.approx(q, rel=1e-9)


def test_area_decreases_with_temperature():
    a_cold = radiator_area(1e6, 350.0, emissivity=0.85)
    a_hot = radiator_area(1e6, 700.0, emissivity=0.85)
    # ~16x smaller for a doubling of temperature.
    assert a_hot < a_cold
    assert a_cold / a_hot == pytest.approx(16.0, rel=0.02)


def test_absorbed_flux_increases_area():
    a0 = radiator_area(1e6, 350.0, emissivity=0.85, absorbed_flux=0.0)
    a1 = radiator_area(1e6, 350.0, emissivity=0.85, absorbed_flux=100.0)
    assert a1 > a0


def test_absorbed_flux_too_high_raises():
    with pytest.raises(ValueError):
        # At 300 K the gross flux is ~390 W/m2; 1000 absorbed is impossible.
        radiator_area(1e6, 300.0, emissivity=0.85, absorbed_flux=1000.0)


def test_negative_temperature_rejected():
    with pytest.raises(ValueError):
        radiated_power(1.0, -10.0, 1.0)


def test_emissivity_out_of_range_rejected():
    with pytest.raises(ValueError):
        radiated_power(1.0, 300.0, 1.5)


def test_panel_mass_proportional_to_area():
    r = size_panel_radiator(1e6, 400.0, areal_density_kg_m2=7.0)
    assert r.mass_kg == pytest.approx(r.area_m2 * 7.0, rel=1e-9)


def test_droplet_lighter_than_panel():
    drop = size_droplet_radiator(1e6, 500.0)
    panel = size_panel_radiator(1e6, 500.0)
    assert drop.mass_kg < panel.mass_kg


def test_droplet_loss_fraction_bounded():
    drop = size_droplet_radiator(1e6, 500.0)
    assert 0.0 <= drop.evaporative_loss_fraction <= 1.0


def test_liquid_sheet_mass_grows_with_thickness():
    thin = size_liquid_sheet_radiator(1e6, 500.0, film_thickness_m=5e-5)
    thick = size_liquid_sheet_radiator(1e6, 500.0, film_thickness_m=5e-4)
    assert thick.fluid_mass_kg > thin.fluid_mass_kg


def test_metamaterial_emissivity_bounded_benefit():
    sweep = metamaterial_emissivity_sweep(1e6, 350.0)
    # Going 0.5 -> 1.0 can at most halve the area (factor 2).
    ratio = sweep["area_m2"][0] / sweep["area_m2"][-1]
    assert ratio == pytest.approx(2.0, rel=0.02)
