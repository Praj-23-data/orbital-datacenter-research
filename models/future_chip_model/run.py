"""MODEL 7 -- Semiconductor co-design (future chips).

Sweeps allowable junction temperature and compares semiconductors, producing
temperature vs radiator area, mass, launch mass and launch cost. This is the
study's central result: junction temperature is a stronger lever than radiator
technology.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from simulations.economics import MassBreakdown, deployment_cost, power_generation_mass
from simulations.semiconductors import (
    ThermalBudget,
    junction_temperature_sweep,
    material_comparison_table,
)
from models.config import BaseConfig


def run(config: BaseConfig | None = None) -> dict:
    cfg = config or BaseConfig()
    budget = ThermalBudget(
        cfg.junction_to_coolant_k, cfg.coolant_rise_k, cfg.coolant_to_radiator_k
    )
    tj = np.linspace(380.0, 1100.0, 30)
    sweep = junction_temperature_sweep(
        cfg.heat_to_reject_w, tj, emissivity=cfg.emissivity,
        areal_density_kg_m2=cfg.areal_density_kg_m2, budget=budget,
    )
    pv_mass = power_generation_mass(cfg.compute_power_w, cfg.pv_specific_power_w_per_kg)
    costs = []
    for _, r in sweep.iterrows():
        mb = MassBreakdown(
            radiator_kg=r["radiator_mass_kg"], coolant_kg=cfg.coolant_kg,
            structure_kg=cfg.structure_kg, power_generation_kg=pv_mass,
        )
        c = deployment_cost(
            cfg.compute_power_w, cfg.heat_to_reject_w, mb,
            launch_cost_usd_per_kg=cfg.launch_cost_usd_per_kg,
        )
        costs.append({"total_mass_kg": c.total_mass_kg,
                      "deployment_cost_usd": c.deployment_cost_usd,
                      "cost_per_mw_usd": c.cost_per_mw_compute_usd})
    sweep = pd.concat([sweep.reset_index(drop=True), pd.DataFrame(costs)], axis=1)
    return {"sweep": sweep,
            "material_table": material_comparison_table(cfg.heat_to_reject_w)}


if __name__ == "__main__":
    out = run()
    pd.set_option("display.width", 220)
    print(out["material_table"].to_string(index=False))
