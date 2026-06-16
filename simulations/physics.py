"""Core governing equations for orbital thermal management.

Every function here is a faithful, dimensionally-consistent implementation of
a first-principles relation. **No correlations, no fudge factors, no
atmospheric heat paths.** In vacuum the *only* way to reject heat is thermal
radiation, and that constraint is encoded directly in :func:`radiator_area`.

Governing relations implemented
-------------------------------
1. Stefan-Boltzmann radiation         P = e * sigma * A * (T^4 - T_sink^4)
2. Convective/advective heat transport Q = m_dot * Cp * dT
3. Thermal resistance                 R = dT / Q
4. Steady-state energy balance        P_in = P_out
5. Solar (and environmental) loading  P_abs = alpha * S * A_proj

Symbolic cross-check
--------------------
:func:`symbolic_stefan_boltzmann` returns the SymPy expression so notebooks
and tests can verify the algebra and units symbolically rather than trusting
the numeric code blindly.

References
----------
[1] Incropera & DeWitt, *Fundamentals of Heat and Mass Transfer*, 7th ed.
[2] Gilmore, D. (2002) *Spacecraft Thermal Control Handbook*, AIAA.
[3] Modest, M. (2013) *Radiative Heat Transfer*, 3rd ed., Academic Press.
"""

from __future__ import annotations

from typing import Optional

import sympy as sp

from .constants import DEEP_SPACE_TEMPERATURE, STEFAN_BOLTZMANN
from .units import (
    require_fraction,
    require_non_negative,
    require_positive,
    require_temperature_kelvin,
)


# --------------------------------------------------------------------------
# 1. Stefan-Boltzmann radiation
# --------------------------------------------------------------------------
def radiated_power(
    area: float,
    temperature: float,
    emissivity: float = 1.0,
    sink_temperature: float = DEEP_SPACE_TEMPERATURE,
    radiating_sides: int = 1,
) -> float:
    """Net radiative power rejected by a grey surface to a cold sink.

    .. math::
        P = \\varepsilon\\,\\sigma\\,A_\\mathrm{eff}\\,(T^4 - T_\\mathrm{sink}^4)

    Parameters
    ----------
    area : float
        Physical (one-sided) radiating area, m^2.
    temperature : float
        Surface temperature, K (must be > 0).
    emissivity : float
        Hemispherical total emissivity in [0, 1].
    sink_temperature : float
        Temperature of the radiative environment, K. Defaults to the cosmic
        microwave background (2.725 K) -- the coldest available sink.
    radiating_sides : int
        1 for a panel that radiates from one face, 2 for an isothermal panel
        exposed to space on both faces. ``A_eff = area * radiating_sides``.

    Returns
    -------
    float
        Net radiated power, W. Positive means heat leaves the surface.
    """
    require_positive(area, "area")
    require_temperature_kelvin(temperature, "temperature")
    require_temperature_kelvin(sink_temperature, "sink_temperature")
    require_fraction(emissivity, "emissivity")
    if radiating_sides not in (1, 2):
        raise ValueError("radiating_sides must be 1 or 2.")

    effective_area = area * radiating_sides
    return (
        emissivity
        * STEFAN_BOLTZMANN
        * effective_area
        * (temperature**4 - sink_temperature**4)
    )


def radiator_area(
    heat_to_reject: float,
    temperature: float,
    emissivity: float = 1.0,
    sink_temperature: float = DEEP_SPACE_TEMPERATURE,
    radiating_sides: int = 1,
    absorbed_flux: float = 0.0,
) -> float:
    """Physical radiator area required to reject a given heat load.

    Inverts the Stefan-Boltzmann law, with an optional environmental
    absorbed-flux penalty (solar + albedo + planetary IR) that *reduces* the
    net rejection capability per unit area:

    .. math::
        A = \\frac{Q}{\\varepsilon\\sigma n (T^4 - T_\\mathrm{sink}^4)
                     - q_\\mathrm{abs}}

    where ``n`` is the number of radiating sides and ``q_abs`` is the net
    absorbed environmental flux per unit physical area (W/m^2).

    Raises
    ------
    ValueError
        If the absorbed environmental flux exceeds the surface's gross
        emissive capability (the radiator cannot reject heat -- it would heat
        up). This is a real failure mode, not a numerical edge case.
    """
    require_positive(heat_to_reject, "heat_to_reject")
    require_temperature_kelvin(temperature, "temperature")
    require_temperature_kelvin(sink_temperature, "sink_temperature")
    require_fraction(emissivity, "emissivity")
    require_non_negative(absorbed_flux, "absorbed_flux")
    if radiating_sides not in (1, 2):
        raise ValueError("radiating_sides must be 1 or 2.")

    gross_flux = (
        emissivity
        * STEFAN_BOLTZMANN
        * radiating_sides
        * (temperature**4 - sink_temperature**4)
    )
    net_flux = gross_flux - absorbed_flux
    if net_flux <= 0:
        raise ValueError(
            "Absorbed environmental flux "
            f"({absorbed_flux:.1f} W/m^2) meets or exceeds the gross emissive "
            f"capability ({gross_flux:.1f} W/m^2) at T={temperature:.1f} K. "
            "The radiator cannot reject heat in this configuration -- raise "
            "the radiator temperature, increase emissivity, or improve the "
            "view to deep space."
        )
    return heat_to_reject / net_flux


def equilibrium_temperature(
    heat_load_flux: float,
    emissivity: float = 1.0,
    absorbed_flux: float = 0.0,
    sink_temperature: float = DEEP_SPACE_TEMPERATURE,
    radiating_sides: int = 1,
) -> float:
    """Steady-state temperature of a surface given net heat flux.

    Solves the energy balance ``q_in = e sigma n (T^4 - T_sink^4)`` for T.
    """
    require_non_negative(heat_load_flux, "heat_load_flux")
    require_fraction(emissivity, "emissivity")
    require_non_negative(absorbed_flux, "absorbed_flux")
    total_in = heat_load_flux + absorbed_flux
    denom = emissivity * STEFAN_BOLTZMANN * radiating_sides
    t4 = total_in / denom + sink_temperature**4
    return t4**0.25


# --------------------------------------------------------------------------
# 2. Heat transport (advection through a coolant loop)
# --------------------------------------------------------------------------
def heat_transport(mass_flow: float, cp: float, delta_t: float) -> float:
    """Sensible heat carried by a coolant stream.

    .. math:: Q = \\dot{m}\\,C_p\\,\\Delta T
    """
    require_positive(mass_flow, "mass_flow")
    require_positive(cp, "cp")
    require_positive(delta_t, "delta_t")
    return mass_flow * cp * delta_t


def required_mass_flow(heat: float, cp: float, delta_t: float) -> float:
    """Coolant mass flow needed to carry ``heat`` across temperature rise dT."""
    require_positive(heat, "heat")
    require_positive(cp, "cp")
    require_positive(delta_t, "delta_t")
    return heat / (cp * delta_t)


# --------------------------------------------------------------------------
# 3. Thermal resistance
# --------------------------------------------------------------------------
def thermal_resistance(delta_t: float, heat: float) -> float:
    """Thermal resistance R = dT / Q  (K/W)."""
    require_positive(heat, "heat")
    require_non_negative(delta_t, "delta_t")
    return delta_t / heat


def conduction_resistance(thickness: float, conductivity: float, area: float) -> float:
    """1-D conduction resistance R = L / (k A)  (K/W)."""
    require_positive(thickness, "thickness")
    require_positive(conductivity, "conductivity")
    require_positive(area, "area")
    return thickness / (conductivity * area)


def temperature_drop(heat: float, resistance: float) -> float:
    """Temperature drop across a resistance: dT = Q * R."""
    require_non_negative(heat, "heat")
    require_non_negative(resistance, "resistance")
    return heat * resistance


# --------------------------------------------------------------------------
# 4. Energy balance
# --------------------------------------------------------------------------
def energy_balance_residual(power_in: float, power_out: float) -> float:
    """Residual P_in - P_out. Zero (within tolerance) at steady state."""
    return power_in - power_out


def is_balanced(power_in: float, power_out: float, rtol: float = 1e-6) -> bool:
    """True if P_in and P_out agree to within ``rtol`` relative tolerance."""
    scale = max(abs(power_in), abs(power_out), 1e-30)
    return abs(power_in - power_out) / scale <= rtol


# --------------------------------------------------------------------------
# 5. Solar / environmental loading
# --------------------------------------------------------------------------
def solar_loading(
    absorptivity: float, irradiance: float, projected_area: float
) -> float:
    """Absorbed solar power P = alpha * S * A_proj  (W).

    ``projected_area`` is the area *facing the Sun*. A radiator flown edge-on
    to the Sun has a small projected area and therefore a small solar load --
    a key design lever in this study.
    """
    require_fraction(absorptivity, "absorptivity")
    require_non_negative(irradiance, "irradiance")
    require_non_negative(projected_area, "projected_area")
    return absorptivity * irradiance * projected_area


# --------------------------------------------------------------------------
# Symbolic cross-checks (used by tests and notebooks)
# --------------------------------------------------------------------------
def symbolic_stefan_boltzmann() -> sp.Eq:
    """Return the Stefan-Boltzmann law as a SymPy equation for verification."""
    eps, sigma, A, T, Ts, P = sp.symbols(
        "varepsilon sigma A T T_sink P", positive=True
    )
    return sp.Eq(P, eps * sigma * A * (T**4 - Ts**4))


def symbolic_radiator_area() -> sp.Expr:
    """Symbolic solution of the SB law for area, to confirm the inversion."""
    eps, sigma, A, T, Ts, Q = sp.symbols(
        "varepsilon sigma A T T_sink Q", positive=True
    )
    eq = sp.Eq(Q, eps * sigma * A * (T**4 - Ts**4))
    return sp.solve(eq, A)[0]


__all__ = [
    "radiated_power",
    "radiator_area",
    "equilibrium_temperature",
    "heat_transport",
    "required_mass_flow",
    "thermal_resistance",
    "conduction_resistance",
    "temperature_drop",
    "energy_balance_residual",
    "is_balanced",
    "solar_loading",
    "symbolic_stefan_boltzmann",
    "symbolic_radiator_area",
]
