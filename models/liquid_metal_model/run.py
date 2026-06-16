"""MODEL 3 -- Coolant comparison (water, ammonia, NaK, lithium, molten salt).

Reports Cp, density, conductivity, pumping requirements, temperature limits and
a ranking table sorted by parasitic pumping fraction.
"""
from __future__ import annotations

import pandas as pd

from simulations.coolant import coolant_ranking_table
from models.config import BaseConfig


def run(config: BaseConfig | None = None) -> pd.DataFrame:
    cfg = config or BaseConfig()
    return coolant_ranking_table(cfg.heat_to_reject_w, cfg.coolant_rise_k)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(run().to_string(index=False))
