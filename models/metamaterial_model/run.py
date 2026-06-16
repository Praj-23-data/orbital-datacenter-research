"""MODEL 6 -- Metamaterial radiators.

Sweeps emissivity 0.5 -> 1.0 and reports the impact on radiator area, mass and
heat-rejection capability. Demonstrates the *bounded* (<=2x) benefit of
emissivity engineering relative to the T^4 benefit of hotter operation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from simulations.constants import CELSIUS_OFFSET
from simulations.radiator import metamaterial_emissivity_sweep
from models.config import BaseConfig


def run(config: BaseConfig | None = None, radiating_temp_c: float = 40.0) -> pd.DataFrame:
    cfg = config or BaseConfig()
    sweep = metamaterial_emissivity_sweep(
        heat_to_reject_w=cfg.heat_to_reject_w,
        radiating_temperature_k=radiating_temp_c + CELSIUS_OFFSET,
        emissivities=np.linspace(0.5, 1.0, 11),
        areal_density_kg_m2=cfg.areal_density_kg_m2,
    )
    return pd.DataFrame(sweep)


if __name__ == "__main__":
    print(run().to_string(index=False))
