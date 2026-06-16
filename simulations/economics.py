"""Economic model for orbital data-centre deployment.

The dominant cost of anything in orbit is *mass to orbit*. This module rolls up
the four mass contributors -- radiator, coolant inventory, structure, and power
generation -- multiplies by a launch cost per kg, and reports deployment cost,
cost per MW of compute, and cost per kW of heat rejected.

The model is deliberately transparent and parametric: every mass term is an
explicit input so sensitivity studies (see :mod:`simulations.sensitivity_analysis`)
can vary launch cost, radiator areal density, junction temperature, etc.

Caveats
-------
* Non-recurring engineering, hardware procurement, and ground/operations costs
  are *not* included by default; this is a launch-mass-dominated lower bound.
  A hardware cost per kg can be supplied to bound the upper end.
* Power-generation mass assumes photovoltaic arrays at a configurable specific
  power (W/kg). Nuclear options would change this term substantially.

References
----------
[1] Jones, H.W. (2018) "The Recent Large Reduction in Space Launch Cost",
    48th Intl. Conf. on Environmental Systems, ICES-2018-81.
[2] NASA State-of-the-Art Small Spacecraft Technology reports (power systems).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .constants import LAUNCH_COST_STARSHIP_TODAY
from .units import require_non_negative, require_positive


@dataclass
class MassBreakdown:
    radiator_kg: float
    coolant_kg: float
    structure_kg: float
    power_generation_kg: float

    @property
    def total_kg(self) -> float:
        return (
            self.radiator_kg
            + self.coolant_kg
            + self.structure_kg
            + self.power_generation_kg
        )


@dataclass
class CostResult:
    total_mass_kg: float
    launch_cost_usd: float
    hardware_cost_usd: float
    deployment_cost_usd: float
    cost_per_mw_compute_usd: float
    cost_per_kw_rejected_usd: float
    mass_breakdown: MassBreakdown


def power_generation_mass(
    electrical_power_w: float, specific_power_w_per_kg: float = 150.0
) -> float:
    """Mass of the power system to generate ``electrical_power_w``.

    Photovoltaic specific power ranges from ~50 W/kg (rigid legacy panels) to
    >1000 W/kg (advanced thin-film roll-out arrays). 150 W/kg is a conservative
    near-term value.
    """
    require_positive(electrical_power_w, "electrical_power_w")
    require_positive(specific_power_w_per_kg, "specific_power_w_per_kg")
    return electrical_power_w / specific_power_w_per_kg


def deployment_cost(
    compute_power_w: float,
    heat_rejected_w: float,
    mass: MassBreakdown,
    launch_cost_usd_per_kg: float = LAUNCH_COST_STARSHIP_TODAY,
    hardware_cost_usd_per_kg: float = 0.0,
) -> CostResult:
    """Roll up total deployment cost from a mass breakdown.

    Parameters
    ----------
    compute_power_w : float
        Electrical compute power (defines cost per MW of compute).
    heat_rejected_w : float
        Heat the radiator must reject (defines cost per kW rejected).
    mass : MassBreakdown
        Component masses (kg).
    launch_cost_usd_per_kg : float
        $/kg to orbit.
    hardware_cost_usd_per_kg : float
        Optional flat hardware cost adder per kg (NRE/procurement proxy).
    """
    require_positive(compute_power_w, "compute_power_w")
    require_positive(heat_rejected_w, "heat_rejected_w")
    require_non_negative(launch_cost_usd_per_kg, "launch_cost_usd_per_kg")
    require_non_negative(hardware_cost_usd_per_kg, "hardware_cost_usd_per_kg")

    total_mass = mass.total_kg
    launch_cost = total_mass * launch_cost_usd_per_kg
    hardware_cost = total_mass * hardware_cost_usd_per_kg
    deployment = launch_cost + hardware_cost

    return CostResult(
        total_mass_kg=total_mass,
        launch_cost_usd=launch_cost,
        hardware_cost_usd=hardware_cost,
        deployment_cost_usd=deployment,
        cost_per_mw_compute_usd=deployment / (compute_power_w / 1e6),
        cost_per_kw_rejected_usd=deployment / (heat_rejected_w / 1e3),
        mass_breakdown=mass,
    )


__all__ = [
    "MassBreakdown",
    "CostResult",
    "power_generation_mass",
    "deployment_cost",
]
