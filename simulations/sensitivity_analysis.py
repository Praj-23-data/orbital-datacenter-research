"""Sensitivity-analysis utilities and trade-space grid generators.

Thin, dependency-light helpers that wrap the physics modules to produce the
arrays and dataframes the notebooks turn into heat maps, contour plots and
trade-space diagrams. Keeping the sweep logic here (rather than in notebooks)
keeps the analysis reproducible and unit-testable.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from .economics import MassBreakdown, deployment_cost, power_generation_mass
from .physics import radiator_area
from .semiconductors import ThermalBudget, radiator_temperature_from_junction


def one_dimensional_sweep(
    func: Callable[[float], float],
    values: np.ndarray,
    name: str = "x",
    output_name: str = "y",
) -> pd.DataFrame:
    """Apply ``func`` across ``values`` and return a tidy two-column frame."""
    return pd.DataFrame(
        {name: np.asarray(values, dtype=float),
         output_name: [func(float(v)) for v in values]}
    )


def junction_vs_launchcost_grid(
    heat_to_reject_w: float,
    compute_power_w: float,
    junction_temps_k: np.ndarray,
    launch_costs_usd_per_kg: np.ndarray,
    emissivity: float = 0.85,
    areal_density_kg_m2: float = 7.0,
    coolant_kg: float = 5000.0,
    structure_kg: float = 20000.0,
    pv_specific_power_w_per_kg: float = 150.0,
    budget: ThermalBudget | None = None,
) -> pd.DataFrame:
    """2-D trade space: deployment cost vs (junction temperature, launch cost).

    Returns a long-form dataframe (one row per grid cell) suitable for pivoting
    into a heat map or contour plot. This is the figure that answers the
    headline question: how much does raising the chip temperature beat cheaper
    launch?
    """
    budget = budget or ThermalBudget()
    pv_mass = power_generation_mass(compute_power_w, pv_specific_power_w_per_kg)
    rows = []
    for tj in junction_temps_k:
        t_rad = radiator_temperature_from_junction(float(tj), budget)
        area = radiator_area(
            heat_to_reject_w, t_rad, emissivity=emissivity, radiating_sides=2
        )
        radiator_mass = area * areal_density_kg_m2
        mass = MassBreakdown(
            radiator_kg=radiator_mass,
            coolant_kg=coolant_kg,
            structure_kg=structure_kg,
            power_generation_kg=pv_mass,
        )
        for lc in launch_costs_usd_per_kg:
            cost = deployment_cost(
                compute_power_w=compute_power_w,
                heat_rejected_w=heat_to_reject_w,
                mass=mass,
                launch_cost_usd_per_kg=float(lc),
            )
            rows.append(
                {
                    "junction_temp_k": float(tj),
                    "launch_cost_usd_per_kg": float(lc),
                    "radiator_area_m2": area,
                    "radiator_mass_kg": radiator_mass,
                    "total_mass_kg": cost.total_mass_kg,
                    "deployment_cost_usd": cost.deployment_cost_usd,
                    "cost_per_mw_usd": cost.cost_per_mw_compute_usd,
                }
            )
    return pd.DataFrame(rows)


def emissivity_vs_temperature_grid(
    heat_to_reject_w: float,
    radiator_temps_k: np.ndarray,
    emissivities: np.ndarray,
) -> pd.DataFrame:
    """2-D grid of radiator area over (radiator temperature, emissivity).

    Used to show, side by side, that temperature (a T^4 lever) dominates
    emissivity (a linear, bounded lever).
    """
    rows = []
    for t in radiator_temps_k:
        for e in emissivities:
            area = radiator_area(
                heat_to_reject_w, float(t), emissivity=float(e), radiating_sides=2
            )
            rows.append(
                {
                    "radiator_temp_k": float(t),
                    "emissivity": float(e),
                    "radiator_area_m2": area,
                }
            )
    return pd.DataFrame(rows)


__all__ = [
    "one_dimensional_sweep",
    "junction_vs_launchcost_grid",
    "emissivity_vs_temperature_grid",
]
