"""Physical and engineering constants used throughout the project.

All values are in **SI units** unless explicitly stated otherwise. Each
constant carries an inline comment giving its unit and a short provenance
note so that downstream code never has to guess.

References
----------
[1] CODATA 2018 recommended values, https://physics.nist.gov/cuu/Constants/
[2] Kopp, G. & Lean, J. (2011) "A new, lower value of total solar
    irradiance", Geophys. Res. Lett. 38, L01706.
[3] Gilmore, D. (2002) *Spacecraft Thermal Control Handbook*, Vol. 1, AIAA.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Fundamental constants
# --------------------------------------------------------------------------
STEFAN_BOLTZMANN: float = 5.670374419e-8  # W m^-2 K^-4  (CODATA 2018)
SPEED_OF_LIGHT: float = 2.99792458e8       # m s^-1
BOLTZMANN: float = 1.380649e-23            # J K^-1
ELEMENTARY_CHARGE: float = 1.602176634e-19  # C (also 1 eV in joules)
EV_TO_JOULE: float = ELEMENTARY_CHARGE      # J per eV

# --------------------------------------------------------------------------
# Thermodynamic reference points
# --------------------------------------------------------------------------
ABS_ZERO_CELSIUS: float = -273.15          # deg C
CELSIUS_OFFSET: float = 273.15             # K added to deg C to get kelvin
DEEP_SPACE_TEMPERATURE: float = 2.725      # K  (CMB; the radiative heat sink)

# --------------------------------------------------------------------------
# Orbital / environmental fluxes (1 AU, near-Earth)
# --------------------------------------------------------------------------
SOLAR_CONSTANT: float = 1361.0             # W m^-2  total solar irradiance [2]
EARTH_ALBEDO: float = 0.30                 # dimensionless, orbit-averaged
EARTH_IR_FLUX_SURFACE: float = 237.0       # W m^-2 outgoing longwave at TOA [3]
EARTH_RADIUS: float = 6.371e6              # m
AU: float = 1.495978707e11                 # m

# --------------------------------------------------------------------------
# Standard gravitational parameter of Earth (for orbital period helpers)
# --------------------------------------------------------------------------
MU_EARTH: float = 3.986004418e14           # m^3 s^-2

# --------------------------------------------------------------------------
# Convenience launch-cost reference scenarios ($ per kg to LEO)
# --------------------------------------------------------------------------
LAUNCH_COST_FALCON9: float = 2700.0        # USD/kg, expendable-class reference
LAUNCH_COST_FALCON_HEAVY: float = 1500.0   # USD/kg
LAUNCH_COST_STARSHIP_TODAY: float = 500.0  # USD/kg, early operational estimate
LAUNCH_COST_STARSHIP_TARGET: float = 100.0  # USD/kg, aspirational

__all__ = [name for name in globals() if name.isupper()]
