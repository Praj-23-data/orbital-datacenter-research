"""Coolant working-fluid models for orbital thermal loops.

Provides a curated property database for five candidate coolants and a
first-principles pumping-power model (Darcy-Weisbach friction in a circular
pipe). Properties are representative mid-range values for the *liquid* phase
near each fluid's useful operating band; they are documented with sources and
should be treated as engineering estimates, not lab-grade tables.

Why these five
--------------
* **Water** -- baseline, excellent Cp, but narrow liquid range and high vapour
  pressure (poor for hot operation or open-loop droplet concepts).
* **Ammonia** -- the ISS workhorse; good Cp, but low boiling point limits hot
  operation.
* **NaK** (eutectic) -- liquid metal, wide liquid range, low vapour pressure;
  enables hot and droplet/sheet radiators.
* **Lithium** -- very high Cp and conductivity, extreme upper temperature
  limit; the high-temperature champion but chemically aggressive.
* **Molten salt** -- stable to high temperature, low vapour pressure, but poor
  thermal conductivity and high pumping cost.

References
----------
[1] Foust, O.J. (1972) *Sodium-NaK Engineering Handbook*, Gordon & Breach.
[2] NIST Chemistry WebBook, https://webbook.nist.gov/
[3] Sohal, M. et al. (2010) "Engineering Database of Liquid Salt
    Thermophysical and Thermochemical Properties", INL/EXT-10-18297.
[4] White, F.M. (2011) *Fluid Mechanics*, 7th ed., McGraw-Hill (Darcy-Weisbach).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .physics import required_mass_flow
from .units import require_positive


@dataclass(frozen=True)
class Coolant:
    """Thermophysical properties of a single-phase liquid coolant.

    All properties are representative values for the liquid phase at a
    temperature within the fluid's useful band. SI units throughout.
    """

    name: str
    cp_j_kg_k: float           # specific heat capacity
    density_kg_m3: float       # liquid density
    thermal_conductivity_w_m_k: float
    dynamic_viscosity_pa_s: float
    melting_point_k: float     # lower liquid limit
    boiling_point_k: float     # upper liquid limit (at ~1 atm unless noted)
    vapour_pressure_pa_at_op: float  # vapour pressure at a representative op T
    molar_mass_kg_mol: float
    note: str = ""

    @property
    def liquid_range_k(self) -> float:
        return self.boiling_point_k - self.melting_point_k


# --------------------------------------------------------------------------
# Property database (liquid-phase, representative)
# --------------------------------------------------------------------------
COOLANTS: dict[str, Coolant] = {
    "water": Coolant(
        name="Water",
        cp_j_kg_k=4186.0,
        density_kg_m3=997.0,
        thermal_conductivity_w_m_k=0.606,
        dynamic_viscosity_pa_s=8.9e-4,
        melting_point_k=273.15,
        boiling_point_k=373.15,
        vapour_pressure_pa_at_op=3.2e3,  # ~25 C
        molar_mass_kg_mol=0.018015,
        note="Baseline; narrow range, high vapour pressure.",
    ),
    "ammonia": Coolant(
        name="Ammonia",
        cp_j_kg_k=4700.0,
        density_kg_m3=610.0,
        thermal_conductivity_w_m_k=0.50,
        dynamic_viscosity_pa_s=1.3e-4,
        melting_point_k=195.4,
        boiling_point_k=239.8,
        vapour_pressure_pa_at_op=1.0e6,  # very high; loops are pressurized
        molar_mass_kg_mol=0.017031,
        note="ISS coolant; excellent Cp, low boiling point.",
    ),
    "nak": Coolant(
        name="NaK (eutectic 22Na-78K)",
        cp_j_kg_k=982.0,
        density_kg_m3=866.0,
        thermal_conductivity_w_m_k=22.0,
        dynamic_viscosity_pa_s=5.0e-4,
        melting_point_k=260.5,
        boiling_point_k=1058.0,
        vapour_pressure_pa_at_op=1.0e-3,  # low at moderate T
        molar_mass_kg_mol=0.0409,
        note="Liquid metal; wide range, low vapour pressure, enables droplet.",
    ),
    "lithium": Coolant(
        name="Lithium",
        cp_j_kg_k=4170.0,
        density_kg_m3=512.0,
        thermal_conductivity_w_m_k=45.0,
        dynamic_viscosity_pa_s=4.0e-4,
        melting_point_k=453.7,
        boiling_point_k=1615.0,
        vapour_pressure_pa_at_op=1.0e-2,
        molar_mass_kg_mol=0.006941,
        note="High-temperature champion; aggressive, must stay molten (>180 C).",
    ),
    "molten_salt": Coolant(
        name="Molten salt (solar salt 60NaNO3-40KNO3)",
        cp_j_kg_k=1500.0,
        density_kg_m3=1899.0,
        thermal_conductivity_w_m_k=0.52,
        dynamic_viscosity_pa_s=3.0e-3,
        melting_point_k=494.0,
        boiling_point_k=873.0,  # decomposition-limited, not a true boil
        vapour_pressure_pa_at_op=1.0e-2,
        molar_mass_kg_mol=0.091,  # mixture-averaged proxy
        note="Stable to high T, low vapour pressure, poor conductivity.",
    ),
}


# --------------------------------------------------------------------------
# Pumping model (Darcy-Weisbach laminar/turbulent)
# --------------------------------------------------------------------------
def reynolds_number(
    mass_flow: float, diameter: float, viscosity: float
) -> float:
    """Pipe Reynolds number Re = 4 m_dot / (pi D mu)."""
    require_positive(diameter, "diameter")
    require_positive(viscosity, "viscosity")
    return 4.0 * mass_flow / (np.pi * diameter * viscosity)


def darcy_friction_factor(reynolds: float) -> float:
    """Darcy friction factor: 64/Re (laminar) or Blasius (turbulent)."""
    if reynolds < 2300:
        return 64.0 / max(reynolds, 1e-9)
    # Blasius correlation, valid ~4e3 < Re < 1e5; adequate for estimates.
    return 0.3164 * reynolds**-0.25


def pumping_power(
    coolant: Coolant,
    heat_w: float,
    delta_t_k: float,
    channel_diameter_m: float = 0.02,
    pipe_length_m: float = 200.0,
    target_velocity_m_s: float = 3.0,
    pump_efficiency: float = 0.6,
) -> dict:
    """Estimate coolant pumping power for a given heat load.

    A 100 MW-class loop moves enormous mass flow; a single pipe cannot carry it
    at a sane velocity. We therefore size a bundle of *parallel channels* to
    hold the per-channel velocity near ``target_velocity_m_s`` (a few m/s, as in
    real liquid loops), then evaluate Darcy-Weisbach friction per channel.

    Pumping power is a *parasitic* load the radiator must also reject, so its
    fraction of the heat load is a key feasibility metric (good designs keep it
    well under ~1%).

    Returns a dict with mass flow, channel count, per-channel velocity/Reynolds,
    pressure drop, pumping power, and pumping fraction of the heat load.
    """
    require_positive(heat_w, "heat_w")
    require_positive(delta_t_k, "delta_t_k")
    require_positive(channel_diameter_m, "channel_diameter_m")
    require_positive(target_velocity_m_s, "target_velocity_m_s")

    m_dot = required_mass_flow(heat_w, coolant.cp_j_kg_k, delta_t_k)
    channel_area = np.pi * (channel_diameter_m / 2.0) ** 2

    # Total flow area required to hold the target velocity, then channel count.
    required_area = m_dot / (coolant.density_kg_m3 * target_velocity_m_s)
    n_channels = max(1, int(np.ceil(required_area / channel_area)))

    # Actual per-channel velocity and flow with the integer channel count.
    velocity = m_dot / (coolant.density_kg_m3 * n_channels * channel_area)
    m_dot_per_channel = m_dot / n_channels
    re = reynolds_number(
        m_dot_per_channel, channel_diameter_m, coolant.dynamic_viscosity_pa_s
    )
    f = darcy_friction_factor(re)
    dp = (
        f
        * (pipe_length_m / channel_diameter_m)
        * 0.5
        * coolant.density_kg_m3
        * velocity**2
    )
    volumetric_flow = m_dot / coolant.density_kg_m3
    p_pump = dp * volumetric_flow / pump_efficiency
    return {
        "coolant": coolant.name,
        "mass_flow_kg_s": m_dot,
        "n_channels": n_channels,
        "velocity_m_s": velocity,
        "reynolds": re,
        "friction_factor": f,
        "pressure_drop_pa": dp,
        "pumping_power_w": p_pump,
        "pumping_fraction_of_load": p_pump / heat_w,
    }


def coolant_ranking_table(
    heat_w: float = 100e6,
    delta_t_k: float = 20.0,
) -> pd.DataFrame:
    """Rank all coolants by pumping cost and key properties for a given load.

    Produces a publication-style comparison table. Lower pumping fraction and
    wider liquid range are better; the table is sorted by pumping fraction.
    """
    rows = []
    for c in COOLANTS.values():
        pp = pumping_power(c, heat_w, delta_t_k)
        rows.append(
            {
                "Coolant": c.name,
                "Cp [J/kg/K]": c.cp_j_kg_k,
                "Density [kg/m3]": c.density_kg_m3,
                "k [W/m/K]": c.thermal_conductivity_w_m_k,
                "Liquid range [K]": c.liquid_range_k,
                "Max liquid T [K]": c.boiling_point_k,
                "Vapour p @op [Pa]": c.vapour_pressure_pa_at_op,
                "Mass flow [kg/s]": pp["mass_flow_kg_s"],
                "Pumping power [W]": pp["pumping_power_w"],
                "Pumping fraction": pp["pumping_fraction_of_load"],
            }
        )
    df = pd.DataFrame(rows)
    return df.sort_values("Pumping fraction").reset_index(drop=True)


__all__ = [
    "Coolant",
    "COOLANTS",
    "reynolds_number",
    "darcy_friction_factor",
    "pumping_power",
    "coolant_ranking_table",
]
