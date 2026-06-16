"""Semiconductor co-design: junction temperature as a radiator-mass lever.

This is the central module of the study. It encodes the hypothesis that the
operating temperature of the *compute* -- specifically the maximum allowable
junction temperature ``T_j`` of the semiconductor -- is a more powerful lever
on orbital radiator mass than any radiator technology improvement, because of
the fourth-power Stefan-Boltzmann scaling.

The thermal stack
-----------------
Heat is generated at the junction and must flow to the radiator surface, which
radiates at temperature ``T_rad``. Between them is a temperature *budget*:

    T_rad = T_j - dT_junction_to_coolant - dT_coolant_rise - dT_coolant_to_radiator

The radiator area scales as ``1 / (T_rad^4 - T_sink^4)``. Therefore raising the
allowable ``T_j`` (which raises ``T_rad``) shrinks the radiator by roughly the
fourth power of the temperature ratio. Going from silicon (~398 K max) to a
wide-bandgap or diamond device (~773-1073 K) can shrink the radiator by an
order of magnitude or more -- a benefit no emissivity improvement (bounded by
0.5 -> 1.0, i.e. 2x) can match.

The counter-pressure: hotter junctions increase leakage and can degrade
reliability, and the *server* electronics (memory, power delivery) may not
tolerate the same temperatures. Those are real and are flagged in the
limitations, but they do not change the radiator-mass physics this module
quantifies.

References
----------
[1] Neudeck, P.G. et al. (2002) "High-temperature electronics -- a role for
    wide bandgap semiconductors?", Proc. IEEE 90(6).
[2] Wong, H. & Iwai, H. (2006) review of high-k and wide-bandgap devices.
[3] Pearton, S.J. et al. (2018) "A review of Ga2O3 materials, processing, and
    devices", Appl. Phys. Rev. 5, 011301.
[4] Wort, C.J.H. & Balmer, R.S. (2008) "Diamond as an electronic material",
    Materials Today 11(1-2).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .constants import CELSIUS_OFFSET, DEEP_SPACE_TEMPERATURE
from .physics import radiator_area
from .units import require_positive, require_temperature_kelvin


@dataclass(frozen=True)
class Semiconductor:
    """Material thermal/electronic properties relevant to orbital co-design."""

    name: str
    bandgap_ev: float
    thermal_conductivity_w_m_k: float
    max_junction_temp_k: float       # device-level practical limit
    radiation_tolerance: str         # qualitative: low / moderate / high / very high
    maturity_trl: int                # 1-9 technology readiness level
    note: str = ""

    @property
    def max_junction_temp_c(self) -> float:
        return self.max_junction_temp_k - CELSIUS_OFFSET


# --------------------------------------------------------------------------
# Semiconductor database
# --------------------------------------------------------------------------
SEMICONDUCTORS: dict[str, Semiconductor] = {
    "silicon": Semiconductor(
        name="Silicon (Si)",
        bandgap_ev=1.12,
        thermal_conductivity_w_m_k=150.0,
        max_junction_temp_k=398.0,        # ~125 C practical
        radiation_tolerance="moderate",
        maturity_trl=9,
        note="Incumbent CMOS; limits hot operation, mature and cheap.",
    ),
    "sic": Semiconductor(
        name="Silicon Carbide (4H-SiC)",
        bandgap_ev=3.26,
        thermal_conductivity_w_m_k=370.0,
        max_junction_temp_k=623.0,        # ~350 C demonstrated power devices
        radiation_tolerance="high",
        maturity_trl=8,
        note="Mature wide-bandgap power devices; high T capable.",
    ),
    "gan": Semiconductor(
        name="Gallium Nitride (GaN)",
        bandgap_ev=3.40,
        thermal_conductivity_w_m_k=160.0,
        max_junction_temp_k=573.0,        # ~300 C
        radiation_tolerance="high",
        maturity_trl=7,
        note="Excellent RF/power; thermal conductivity moderate.",
    ),
    "diamond": Semiconductor(
        name="Diamond semiconductor",
        bandgap_ev=5.47,
        thermal_conductivity_w_m_k=2200.0,
        max_junction_temp_k=1073.0,       # ~800 C theoretical/early devices
        radiation_tolerance="very high",
        maturity_trl=3,
        note="Best conductivity and T limit; doping/fabrication immature.",
    ),
    "ga2o3": Semiconductor(
        name="Gallium Oxide (beta-Ga2O3)",
        bandgap_ev=4.80,
        thermal_conductivity_w_m_k=23.0,  # the Achilles heel
        max_junction_temp_k=773.0,        # high T limited by self-heating
        radiation_tolerance="high",
        maturity_trl=4,
        note="Ultra-wide bandgap, very low thermal conductivity is limiting.",
    ),
}


# --------------------------------------------------------------------------
# Thermal stack: junction temperature -> radiator temperature
# --------------------------------------------------------------------------
@dataclass
class ThermalBudget:
    """Temperature drops between junction and radiating surface (kelvin)."""

    junction_to_coolant_k: float = 25.0
    coolant_rise_k: float = 20.0
    coolant_to_radiator_k: float = 10.0

    @property
    def total_k(self) -> float:
        return (
            self.junction_to_coolant_k
            + self.coolant_rise_k
            + self.coolant_to_radiator_k
        )


def radiator_temperature_from_junction(
    junction_temp_k: float, budget: ThermalBudget | None = None
) -> float:
    """Radiating-surface temperature implied by a max junction temperature."""
    require_temperature_kelvin(junction_temp_k, "junction_temp_k")
    budget = budget or ThermalBudget()
    t_rad = junction_temp_k - budget.total_k
    if t_rad <= 0:
        raise ValueError(
            "Thermal budget exceeds junction temperature; radiator temperature "
            "would be non-physical. Reduce the budget or raise T_j."
        )
    return t_rad


# --------------------------------------------------------------------------
# Co-design sweeps
# --------------------------------------------------------------------------
def junction_temperature_sweep(
    heat_to_reject_w: float,
    junction_temps_k: np.ndarray,
    emissivity: float = 0.85,
    areal_density_kg_m2: float = 7.0,
    budget: ThermalBudget | None = None,
    sink_temperature_k: float = DEEP_SPACE_TEMPERATURE,
    radiating_sides: int = 2,
) -> pd.DataFrame:
    """Sweep junction temperature and report radiator area & mass.

    This is the quantitative heart of the co-design argument. For each junction
    temperature it computes the implied radiating temperature, the required
    radiator area, and the radiator mass. The area column makes the ``T^-4``
    collapse visible directly.
    """
    require_positive(heat_to_reject_w, "heat_to_reject_w")
    budget = budget or ThermalBudget()
    rows = []
    for tj in junction_temps_k:
        t_rad = radiator_temperature_from_junction(float(tj), budget)
        area = radiator_area(
            heat_to_reject_w,
            t_rad,
            emissivity=emissivity,
            sink_temperature=sink_temperature_k,
            radiating_sides=radiating_sides,
        )
        rows.append(
            {
                "junction_temp_k": float(tj),
                "junction_temp_c": float(tj) - CELSIUS_OFFSET,
                "radiator_temp_k": t_rad,
                "radiator_area_m2": area,
                "radiator_mass_kg": area * areal_density_kg_m2,
            }
        )
    df = pd.DataFrame(rows)
    df["area_reduction_vs_coolest"] = df["radiator_area_m2"].iloc[0] / df[
        "radiator_area_m2"
    ]
    return df


def material_comparison_table(
    heat_to_reject_w: float = 100e6,
    emissivity: float = 0.85,
    areal_density_kg_m2: float = 7.0,
    budget: ThermalBudget | None = None,
) -> pd.DataFrame:
    """Compare all semiconductors at their *own* max junction temperature.

    Each material is sized at the radiator temperature its maximum junction
    temperature permits, exposing the order-of-magnitude radiator-mass spread
    between silicon and high-temperature wide-bandgap / diamond devices.
    """
    budget = budget or ThermalBudget()
    rows = []
    for s in SEMICONDUCTORS.values():
        t_rad = radiator_temperature_from_junction(s.max_junction_temp_k, budget)
        area = radiator_area(
            heat_to_reject_w,
            t_rad,
            emissivity=emissivity,
            radiating_sides=2,
        )
        rows.append(
            {
                "Material": s.name,
                "Bandgap [eV]": s.bandgap_ev,
                "k [W/m/K]": s.thermal_conductivity_w_m_k,
                "Max Tj [K]": s.max_junction_temp_k,
                "Max Tj [C]": s.max_junction_temp_c,
                "Radiator T [K]": t_rad,
                "Radiator area [m2]": area,
                "Radiator mass [kg]": area * areal_density_kg_m2,
                "Rad tolerance": s.radiation_tolerance,
                "TRL": s.maturity_trl,
            }
        )
    df = pd.DataFrame(rows)
    base = df.loc[df["Material"].str.startswith("Silicon (Si)"), "Radiator mass [kg]"]
    if not base.empty:
        df["Mass vs silicon"] = df["Radiator mass [kg]"] / base.values[0]
    return df.sort_values("Max Tj [K]").reset_index(drop=True)


__all__ = [
    "Semiconductor",
    "SEMICONDUCTORS",
    "ThermalBudget",
    "radiator_temperature_from_junction",
    "junction_temperature_sweep",
    "material_comparison_table",
]
