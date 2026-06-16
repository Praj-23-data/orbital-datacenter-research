"""MODEL 2 -- High-temperature operation.

Sweeps coolant temperature 40..1000 C and reports radiator area reduction,
mass reduction, and efficiency relative to the 40 C baseline.
"""
from __future__ import annotations

import pandas as pd

from simulations.constants import CELSIUS_OFFSET
from simulations.radiator import size_panel_radiator
from models.config import BaseConfig

TEMPS_C = [40, 100, 250, 500, 750, 1000]


def run(config: BaseConfig | None = None) -> pd.DataFrame:
    cfg = config or BaseConfig()
    rows = []
    for tc in TEMPS_C:
        res = size_panel_radiator(
            heat_to_reject_w=cfg.heat_to_reject_w,
            radiating_temperature_k=tc + CELSIUS_OFFSET,
            emissivity=cfg.emissivity,
            areal_density_kg_m2=cfg.areal_density_kg_m2,
            radiating_sides=cfg.radiating_sides,
        )
        rows.append(
            {"coolant_C": tc, "area_m2": res.area_m2, "mass_kg": res.mass_kg}
        )
    df = pd.DataFrame(rows)
    base_area = df["area_m2"].iloc[0]
    base_mass = df["mass_kg"].iloc[0]
    df["area_reduction_x"] = base_area / df["area_m2"]
    df["mass_reduction_x"] = base_mass / df["mass_kg"]
    return df


if __name__ == "__main__":
    print(run().to_string(index=False))
