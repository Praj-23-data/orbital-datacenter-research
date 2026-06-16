"""Radiator models for vacuum heat rejection.

Contains the baseline pumped-loop panel radiator plus three advanced concepts
that decouple radiating area from structural mass:

* **Droplet radiator** -- a sheet of sub-mm coolant droplets is sprayed
  through space, radiates, and is recollected. Mass scales with the *fluid in
  flight* rather than with rigid panel area.
* **Liquid-sheet radiator** -- a thin continuous film of low-vapour-pressure
  liquid radiates from both faces.
* **Metamaterial / high-emissivity radiator** -- a conventional panel whose
  emissivity is engineered toward unity.

All concepts are sized by the same physics: in vacuum, ``Q = e sigma A (T^4 -
T_sink^4)``. They differ only in their *areal mass* and in second-order
penalties (coolant loss, pumping, structure).

Key physical caveat for droplet/sheet radiators
-----------------------------------------------
The coolant must have an extremely low vapour pressure at operating
temperature, otherwise evaporative mass loss in vacuum is prohibitive. This is
why liquid-metal and low-vapour-pressure oils dominate the literature. The
:func:`droplet_evaporative_loss_fraction` helper exposes this sensitivity.

References
----------
[1] Mattick, A.T. & Hertzberg, A. (1981) "Liquid droplet radiators for heat
    rejection in space", J. Energy 5(6).
[2] White, K.A. (1987) "Liquid Droplet Radiator Development Status", NASA
    TM-89852.
[3] Totani, T. et al. (2002) "Numerical and Experimental Studies on Liquid
    Sheet Radiator", J. Thermophysics and Heat Transfer.
[4] Gilmore, D. (2002) *Spacecraft Thermal Control Handbook*, AIAA.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .constants import DEEP_SPACE_TEMPERATURE, STEFAN_BOLTZMANN
from .physics import radiator_area
from .units import require_fraction, require_positive, require_temperature_kelvin


# --------------------------------------------------------------------------
# Baseline panel radiator
# --------------------------------------------------------------------------
@dataclass
class PanelRadiatorResult:
    """Container for a sized panel radiator."""

    area_m2: float
    mass_kg: float
    radiating_temperature_k: float
    emissivity: float
    areal_density_kg_m2: float
    rejected_power_w: float
    specific_rejection_w_per_kg: float


def size_panel_radiator(
    heat_to_reject_w: float,
    radiating_temperature_k: float,
    emissivity: float = 0.85,
    areal_density_kg_m2: float = 7.0,
    sink_temperature_k: float = DEEP_SPACE_TEMPERATURE,
    radiating_sides: int = 2,
    absorbed_flux_w_m2: float = 0.0,
) -> PanelRadiatorResult:
    """Size a conventional two-sided pumped-loop panel radiator.

    Parameters
    ----------
    heat_to_reject_w : float
        Thermal load to reject, W.
    radiating_temperature_k : float
        Effective radiating (panel) temperature, K. This is the *coolant/panel*
        temperature, which is below the chip junction temperature by the
        junction-to-radiator thermal budget (see :mod:`simulations.semiconductors`).
    emissivity : float
        Surface total hemispherical emissivity.
    areal_density_kg_m2 : float
        Radiator mass per unit physical area. Typical deployed pumped-loop
        radiators are ~5-12 kg/m^2 [4]; 7 is a representative midpoint.
    radiating_sides : int
        1 or 2 (two-sided isothermal panel by default).
    absorbed_flux_w_m2 : float
        Net absorbed environmental flux (solar+albedo+IR) per physical area.
    """
    require_positive(heat_to_reject_w, "heat_to_reject_w")
    require_positive(areal_density_kg_m2, "areal_density_kg_m2")
    area = radiator_area(
        heat_to_reject=heat_to_reject_w,
        temperature=radiating_temperature_k,
        emissivity=emissivity,
        sink_temperature=sink_temperature_k,
        radiating_sides=radiating_sides,
        absorbed_flux=absorbed_flux_w_m2,
    )
    mass = area * areal_density_kg_m2
    return PanelRadiatorResult(
        area_m2=area,
        mass_kg=mass,
        radiating_temperature_k=radiating_temperature_k,
        emissivity=emissivity,
        areal_density_kg_m2=areal_density_kg_m2,
        rejected_power_w=heat_to_reject_w,
        specific_rejection_w_per_kg=heat_to_reject_w / mass,
    )


# --------------------------------------------------------------------------
# Droplet radiator
# --------------------------------------------------------------------------
@dataclass
class DropletRadiatorResult:
    droplet_diameter_m: float
    droplet_velocity_m_s: float
    travel_distance_m: float
    residence_time_s: float
    effective_area_m2: float
    fluid_mass_in_flight_kg: float
    evaporative_loss_fraction: float
    mass_kg: float
    rejected_power_w: float


def droplet_residence_time(travel_distance_m: float, velocity_m_s: float) -> float:
    """Time a droplet spends radiating between generator and collector."""
    require_positive(travel_distance_m, "travel_distance_m")
    require_positive(velocity_m_s, "velocity_m_s")
    return travel_distance_m / velocity_m_s


def droplet_effective_area(
    heat_to_reject_w: float,
    radiating_temperature_k: float,
    emissivity: float = 0.95,
    sink_temperature_k: float = DEEP_SPACE_TEMPERATURE,
) -> float:
    """Total droplet surface area required (droplets radiate from full sphere).

    Droplets present their entire spherical surface to space, so the geometric
    efficiency is excellent; ``radiating_sides`` is effectively folded into the
    spherical surface bookkeeping handled by the caller.
    """
    return radiator_area(
        heat_to_reject=heat_to_reject_w,
        temperature=radiating_temperature_k,
        emissivity=emissivity,
        sink_temperature=sink_temperature_k,
        radiating_sides=1,
    )


def droplet_evaporative_loss_fraction(
    vapour_pressure_pa: float,
    molar_mass_kg_mol: float,
    temperature_k: float,
    residence_time_s: float,
    droplet_diameter_m: float,
    liquid_density_kg_m3: float,
    accommodation_coeff: float = 1.0,
) -> float:
    """Fraction of droplet mass lost to vacuum evaporation during flight.

    Uses the Hertz-Knudsen maximum evaporation flux

    .. math::
        \\dot{m}'' = \\alpha\\, p_v \\sqrt{\\frac{M}{2\\pi R T}}

    integrated over the droplet residence time, relative to the droplet mass.
    This is an *upper bound* on loss (alpha=1 gives the kinetic-theory maximum).
    It is the single most important feasibility driver for droplet radiators:
    coolants with non-negligible vapour pressure are disqualified.
    """
    R_GAS = 8.314462618  # J/(mol K)
    require_positive(temperature_k, "temperature_k")
    require_positive(droplet_diameter_m, "droplet_diameter_m")
    require_positive(liquid_density_kg_m3, "liquid_density_kg_m3")
    flux = (
        accommodation_coeff
        * vapour_pressure_pa
        * np.sqrt(molar_mass_kg_mol / (2.0 * np.pi * R_GAS * temperature_k))
    )  # kg m^-2 s^-1
    radius = droplet_diameter_m / 2.0
    surface_area = 4.0 * np.pi * radius**2
    volume = (4.0 / 3.0) * np.pi * radius**3
    droplet_mass = liquid_density_kg_m3 * volume
    lost = flux * surface_area * residence_time_s
    return float(min(lost / droplet_mass, 1.0))


def size_droplet_radiator(
    heat_to_reject_w: float,
    radiating_temperature_k: float,
    droplet_diameter_m: float = 3.0e-4,
    droplet_velocity_m_s: float = 12.0,
    travel_distance_m: float = 10.0,
    liquid_density_kg_m3: float = 870.0,
    emissivity: float = 0.95,
    vapour_pressure_pa: float = 1e-6,
    molar_mass_kg_mol: float = 0.0409,
    sink_temperature_k: float = DEEP_SPACE_TEMPERATURE,
) -> DropletRadiatorResult:
    """Size a liquid-droplet radiator.

    The mass figure of merit is the *fluid in flight* plus a small generator/
    collector allowance, which is far lighter than rigid panels of equal area.
    Defaults correspond to a NaK-like low-vapour-pressure coolant.
    """
    require_positive(droplet_diameter_m, "droplet_diameter_m")
    t_res = droplet_residence_time(travel_distance_m, droplet_velocity_m_s)
    eff_area = droplet_effective_area(
        heat_to_reject_w, radiating_temperature_k, emissivity, sink_temperature_k
    )
    # Fluid in flight: surface-area-to-volume of droplet sheet.
    radius = droplet_diameter_m / 2.0
    # Number of droplets needed for the effective area; each contributes
    # surface 4 pi r^2 and volume (4/3) pi r^3 -> volume = eff_area * r / 3.
    fluid_volume = eff_area * radius / 3.0
    fluid_mass = fluid_volume * liquid_density_kg_m3
    loss = droplet_evaporative_loss_fraction(
        vapour_pressure_pa=vapour_pressure_pa,
        molar_mass_kg_mol=molar_mass_kg_mol,
        temperature_k=radiating_temperature_k,
        residence_time_s=t_res,
        droplet_diameter_m=droplet_diameter_m,
        liquid_density_kg_m3=liquid_density_kg_m3,
    )
    # Generator + collector structural allowance (empirical, kept explicit).
    structure_mass = 0.25 * fluid_mass
    total_mass = fluid_mass + structure_mass
    return DropletRadiatorResult(
        droplet_diameter_m=droplet_diameter_m,
        droplet_velocity_m_s=droplet_velocity_m_s,
        travel_distance_m=travel_distance_m,
        residence_time_s=t_res,
        effective_area_m2=eff_area,
        fluid_mass_in_flight_kg=fluid_mass,
        evaporative_loss_fraction=loss,
        mass_kg=total_mass,
        rejected_power_w=heat_to_reject_w,
    )


# --------------------------------------------------------------------------
# Liquid-sheet radiator
# --------------------------------------------------------------------------
@dataclass
class LiquidSheetRadiatorResult:
    film_thickness_m: float
    area_m2: float
    fluid_mass_kg: float
    structural_mass_kg: float
    mass_kg: float
    rejected_power_w: float


def size_liquid_sheet_radiator(
    heat_to_reject_w: float,
    radiating_temperature_k: float,
    film_thickness_m: float = 1.0e-4,
    liquid_density_kg_m3: float = 870.0,
    emissivity: float = 0.92,
    structural_areal_density_kg_m2: float = 0.5,
    sink_temperature_k: float = DEEP_SPACE_TEMPERATURE,
) -> LiquidSheetRadiatorResult:
    """Size a thin liquid-sheet (film) radiator radiating from both faces."""
    require_positive(film_thickness_m, "film_thickness_m")
    area = radiator_area(
        heat_to_reject=heat_to_reject_w,
        temperature=radiating_temperature_k,
        emissivity=emissivity,
        sink_temperature=sink_temperature_k,
        radiating_sides=2,
    )
    fluid_mass = area * film_thickness_m * liquid_density_kg_m3
    structural_mass = area * structural_areal_density_kg_m2
    return LiquidSheetRadiatorResult(
        film_thickness_m=film_thickness_m,
        area_m2=area,
        fluid_mass_kg=fluid_mass,
        structural_mass_kg=structural_mass,
        mass_kg=fluid_mass + structural_mass,
        rejected_power_w=heat_to_reject_w,
    )


# --------------------------------------------------------------------------
# Metamaterial / engineered-emissivity radiator
# --------------------------------------------------------------------------
def metamaterial_emissivity_sweep(
    heat_to_reject_w: float,
    radiating_temperature_k: float,
    emissivities: Optional[np.ndarray] = None,
    areal_density_kg_m2: float = 7.0,
    sink_temperature_k: float = DEEP_SPACE_TEMPERATURE,
    radiating_sides: int = 2,
) -> dict:
    """Sweep emissivity (0.5 -> 1.0) and report area/mass impact.

    Returns a dict of numpy arrays so callers can tabulate or plot. Because the
    area scales as ``1/emissivity``, the *maximum* achievable improvement from
    emissivity alone is the ratio of the endpoints (e.g. 0.5 -> 1.0 halves the
    area). This bounds how much radiator technology -- as opposed to operating
    temperature -- can ever buy.
    """
    if emissivities is None:
        emissivities = np.linspace(0.5, 1.0, 11)
    areas = np.array(
        [
            radiator_area(
                heat_to_reject_w,
                radiating_temperature_k,
                emissivity=float(e),
                sink_temperature=sink_temperature_k,
                radiating_sides=radiating_sides,
            )
            for e in emissivities
        ]
    )
    masses = areas * areal_density_kg_m2
    return {
        "emissivity": np.asarray(emissivities, dtype=float),
        "area_m2": areas,
        "mass_kg": masses,
        "area_reduction_vs_min": areas[0] / areas,
    }


__all__ = [
    "PanelRadiatorResult",
    "size_panel_radiator",
    "DropletRadiatorResult",
    "droplet_residence_time",
    "droplet_effective_area",
    "droplet_evaporative_loss_fraction",
    "size_droplet_radiator",
    "LiquidSheetRadiatorResult",
    "size_liquid_sheet_radiator",
    "metamaterial_emissivity_sweep",
]
