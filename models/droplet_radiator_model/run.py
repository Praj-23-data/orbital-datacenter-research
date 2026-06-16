"""MODEL 4 -- Droplet radiator.

Models droplet diameter, velocity, travel distance, residence time, recovery
efficiency, effective radiative area, coolant-loss sensitivity, and the mass
reduction versus a solid panel at the same temperature.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from simulations.coolant import COOLANTS
from simulations.constants import CELSIUS_OFFSET
from simulations.radiator import size_droplet_radiator, size_panel_radiator
from models.config import BaseConfig


def run(config: BaseConfig | None = None, radiating_temp_c: float = 250.0) -> dict:
    cfg = config or BaseConfig()
    t_rad = radiating_temp_c + CELSIUS_OFFSET
    nak = COOLANTS["nak"]
    drop = size_droplet_radiator(
        heat_to_reject_w=cfg.heat_to_reject_w,
        radiating_temperature_k=t_rad,
        liquid_density_kg_m3=nak.density_kg_m3,
        vapour_pressure_pa=nak.vapour_pressure_pa_at_op,
        molar_mass_kg_mol=nak.molar_mass_kg_mol,
    )
    panel = size_panel_radiator(
        cfg.heat_to_reject_w, t_rad, emissivity=cfg.emissivity,
        areal_density_kg_m2=cfg.areal_density_kg_m2,
    )
    # Coolant-loss sensitivity to droplet diameter.
    diam = np.array([1e-4, 2e-4, 3e-4, 5e-4, 1e-3])
    loss = [
        size_droplet_radiator(
            cfg.heat_to_reject_w, t_rad, droplet_diameter_m=float(d),
            liquid_density_kg_m3=nak.density_kg_m3,
            vapour_pressure_pa=nak.vapour_pressure_pa_at_op,
            molar_mass_kg_mol=nak.molar_mass_kg_mol,
        ).evaporative_loss_fraction
        for d in diam
    ]
    return {
        "radiating_temperature_C": radiating_temp_c,
        "effective_area_m2": drop.effective_area_m2,
        "residence_time_s": drop.residence_time_s,
        "fluid_mass_in_flight_kg": drop.fluid_mass_in_flight_kg,
        "droplet_mass_kg": drop.mass_kg,
        "panel_mass_kg": panel.mass_kg,
        "mass_reduction_vs_panel_x": panel.mass_kg / drop.mass_kg,
        "evaporative_loss_fraction": drop.evaporative_loss_fraction,
        "loss_sensitivity": pd.DataFrame(
            {"droplet_diameter_m": diam, "loss_fraction": loss}
        ),
    }


if __name__ == "__main__":
    out = run()
    for k, v in out.items():
        if isinstance(v, pd.DataFrame):
            print(f"{k}:\n{v.to_string(index=False)}")
        else:
            print(f"{k:32s}: {v:,.4g}" if isinstance(v, float) else f"{k}: {v}")
