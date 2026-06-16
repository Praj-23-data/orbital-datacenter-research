"""Orbital thermal environment models for LEO, MEO and GEO.

Computes the environmental heat fluxes a radiator must contend with at each
orbit regime: direct solar, Earth-reflected solar (albedo), and Earth infrared
(planetary IR). It also estimates eclipse fraction (which *helps* a radiator,
since it removes the solar load but also removes power generation) and the
recommended radiator orientation.

The central design insight encoded here: **GEO is the kindest environment for
a radiator** because Earth subtends a tiny solid angle, so planetary IR and
albedo loads are nearly zero and the radiator sees almost pure deep space. LEO
is the harshest (strong, time-varying albedo and IR) but offers the cheapest
launch and best latency for many workloads -- a genuine trade.

Method
------
Environmental fluxes onto a surface scale with the *view factor* to Earth,
which falls off with altitude. We use the standard spherical-cap view factor
for a flat plate facing a sphere of radius R at orbital radius r:

.. math:: F = \\left(\\frac{R}{r}\\right)^2

This is the classic first-order approximation used in early thermal sizing
[1,2]. A radiator oriented edge-on to the Sun and broadside to deep space sees
solar only on its (small) projected edge.

References
----------
[1] Gilmore, D. (2002) *Spacecraft Thermal Control Handbook*, AIAA, ch. 2.
[2] Karam, R.D. (1998) *Satellite Thermal Control for Systems Engineers*, AIAA.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .constants import (
    EARTH_ALBEDO,
    EARTH_IR_FLUX_SURFACE,
    EARTH_RADIUS,
    MU_EARTH,
    SOLAR_CONSTANT,
)
from .units import require_fraction, require_positive


@dataclass(frozen=True)
class OrbitRegime:
    name: str
    altitude_m: float

    @property
    def orbital_radius_m(self) -> float:
        return EARTH_RADIUS + self.altitude_m

    @property
    def earth_view_factor(self) -> float:
        """First-order flat-plate-to-sphere view factor (R/r)^2."""
        return (EARTH_RADIUS / self.orbital_radius_m) ** 2

    @property
    def orbital_period_s(self) -> float:
        """Keplerian circular orbital period."""
        r = self.orbital_radius_m
        return 2.0 * np.pi * np.sqrt(r**3 / MU_EARTH)

    @property
    def eclipse_fraction(self) -> float:
        """Fraction of orbit in Earth's shadow (cylindrical shadow model).

        For a circular orbit the maximum eclipse half-angle is
        ``arcsin(R/r)``; the eclipse fraction is that arc over pi. GEO and
        higher have small eclipse fractions; LEO ~ 0.38.
        """
        r = self.orbital_radius_m
        half_angle = np.arcsin(min(EARTH_RADIUS / r, 1.0))
        return float(half_angle / np.pi)


ORBITS: dict[str, OrbitRegime] = {
    "LEO": OrbitRegime(name="Low Earth Orbit", altitude_m=500e3),
    "MEO": OrbitRegime(name="Medium Earth Orbit", altitude_m=20_200e3),
    "GEO": OrbitRegime(name="Geostationary Orbit", altitude_m=35_786e3),
}


@dataclass
class EnvironmentLoads:
    regime: str
    solar_flux_w_m2: float
    albedo_flux_w_m2: float
    earth_ir_flux_w_m2: float
    total_absorbed_flux_w_m2: float
    eclipse_fraction: float
    orbital_period_min: float


def environmental_fluxes(
    orbit: OrbitRegime,
    solar_absorptivity: float = 0.10,
    ir_emissivity: float = 0.85,
    radiator_edge_on_to_sun: bool = True,
    sun_facing_fraction: float = 0.0,
) -> EnvironmentLoads:
    """Net absorbed environmental flux on a radiator surface (W/m^2).

    Parameters
    ----------
    solar_absorptivity : float
        Solar absorptance ``alpha`` of the radiator coating. Radiators use
        low-alpha / high-emissivity optical coatings (e.g. silvered Teflon,
        alpha~0.08-0.15) to reject sunlight.
    ir_emissivity : float
        Infrared emissivity, governs absorption of Earth IR (Kirchhoff).
    radiator_edge_on_to_sun : bool
        If True, the broad radiating face is edge-on to the Sun and the direct
        solar load is taken on the small edge only (``sun_facing_fraction``).
    sun_facing_fraction : float
        Projected sun-facing area as a fraction of the radiating face area
        when edge-on (geometry/pointing-error allowance).

    Returns
    -------
    EnvironmentLoads
        Per-unit-area absorbed fluxes and orbit timing.
    """
    require_fraction(solar_absorptivity, "solar_absorptivity")
    require_fraction(ir_emissivity, "ir_emissivity")

    vf = orbit.earth_view_factor

    # Direct solar on the radiating face.
    if radiator_edge_on_to_sun:
        solar = solar_absorptivity * SOLAR_CONSTANT * sun_facing_fraction
    else:
        solar = solar_absorptivity * SOLAR_CONSTANT

    # Albedo: reflected sunlight, scaled by view factor to Earth.
    albedo = solar_absorptivity * EARTH_ALBEDO * SOLAR_CONSTANT * vf

    # Earth IR: planetary longwave, absorbed per Kirchhoff (alpha_IR = emissivity).
    earth_ir = ir_emissivity * EARTH_IR_FLUX_SURFACE * vf

    total = solar + albedo + earth_ir
    return EnvironmentLoads(
        regime=orbit.name,
        solar_flux_w_m2=solar,
        albedo_flux_w_m2=albedo,
        earth_ir_flux_w_m2=earth_ir,
        total_absorbed_flux_w_m2=total,
        eclipse_fraction=orbit.eclipse_fraction,
        orbital_period_min=orbit.orbital_period_s / 60.0,
    )


def compare_orbits(**kwargs) -> list[EnvironmentLoads]:
    """Return environmental loads for LEO, MEO and GEO with shared settings."""
    return [environmental_fluxes(o, **kwargs) for o in ORBITS.values()]


__all__ = [
    "OrbitRegime",
    "ORBITS",
    "EnvironmentLoads",
    "environmental_fluxes",
    "compare_orbits",
]
