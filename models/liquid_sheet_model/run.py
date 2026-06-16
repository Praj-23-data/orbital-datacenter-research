"""MODEL 5 -- Liquid-sheet radiator.

Models film thickness, surface area, radiative output, and structural mass,
with a sensitivity analysis over film thickness.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from simulations.coolant import COOLANTS
from simulations.constants import CELSIUS_OFFSET
from simulations.radiator import size_liquid_sheet_radiator, size_panel_radiator
from models.config import BaseConfig


def run(config: BaseConfig | None = None, radiating_temp_c: float = 250.0) -> dict:
    cfg = config or BaseConfig()
    t_rad = radiating_temp_c + CELSIUS_OFFSET
    nak = COOLANTS["nak"]
    thicknesses = np.array([2e-5, 5e-5, 1e-4, 2e-4, 5e-4])
    rows = []
    for th in thicknesses:
        s = size_liquid_sheet_radiator(
            cfg.heat_to_reject_w, t_rad, film_thickness_m=float(th),
            liquid_density_kg_m3=nak.density_kg_m3,
        )
        rows.append(
            {"film_thickness_m": float(th), "area_m2": s.area_m2,
             "fluid_mass_kg": s.fluid_mass_kg,
             "structural_mass_kg": s.structural_mass_kg, "total_mass_kg": s.mass_kg}
        )
    df = pd.DataFrame(rows)
    panel = size_panel_radiator(
        cfg.heat_to_reject_w, t_rad, emissivity=cfg.emissivity,
        areal_density_kg_m2=cfg.areal_density_kg_m2,
    )
    return {"radiating_temperature_C": radiating_temp_c,
            "panel_mass_kg": panel.mass_kg, "sensitivity": df}


if __name__ == "__main__":
    out = run()
    print("panel_mass_kg:", round(out["panel_mass_kg"], 1))
    print(out["sensitivity"].to_string(index=False))
