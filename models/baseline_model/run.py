"""MODEL 1 -- Baseline orbital data centre.

100 MW, silicon chips, water cooling, 40 C coolant, traditional radiator.
Outputs: required radiator area, radiator mass, power density, thermal
efficiency.
"""
from __future__ import annotations

from simulations.constants import CELSIUS_OFFSET
from simulations.materials import fin_efficiency
from simulations.radiator import size_panel_radiator
from models.config import BaseConfig


def run(config: BaseConfig | None = None) -> dict:
    cfg = config or BaseConfig()
    coolant_temp_k = 40.0 + CELSIUS_OFFSET  # 40 C water coolant
    res = size_panel_radiator(
        heat_to_reject_w=cfg.heat_to_reject_w,
        radiating_temperature_k=coolant_temp_k,
        emissivity=cfg.emissivity,
        areal_density_kg_m2=cfg.areal_density_kg_m2,
        radiating_sides=cfg.radiating_sides,
    )
    eta_fin = fin_efficiency(0.15, 0.002, 167.0, cfg.emissivity, coolant_temp_k)
    out = {
        "coolant_temperature_C": 40.0,
        "radiator_area_m2": res.area_m2,
        "radiator_mass_kg": res.mass_kg,
        "radiator_mass_tonnes": res.mass_kg / 1000.0,
        "power_density_w_per_m2": cfg.heat_to_reject_w / res.area_m2,
        "specific_rejection_w_per_kg": res.specific_rejection_w_per_kg,
        "radiative_efficiency": cfg.emissivity,   # vs ideal blackbody
        "fin_efficiency": eta_fin,
        "effective_efficiency": cfg.emissivity * eta_fin,
    }
    return out


if __name__ == "__main__":
    for k, v in run().items():
        print(f"{k:32s}: {v:,.4g}" if isinstance(v, float) else f"{k:32s}: {v}")
