"""orbital-datacenter-research simulation package.

A first-principles thermal/economics framework for evaluating the feasibility
of 100 MW - 1 GW data centres operating in vacuum, where heat rejection is by
thermal radiation alone.

Public submodules
------------------
constants               Physical constants (SI).
units                   Unit validation and temperature conversions.
physics                 Governing equations (Stefan-Boltzmann, transport, ...).
radiator                Panel, droplet, liquid-sheet, metamaterial radiators.
coolant                 Coolant property database and pumping model.
orbital_environment     LEO/MEO/GEO environmental loads and eclipse.
materials               Structural materials, coatings, fin efficiency.
semiconductors          Junction-temperature co-design (central module).
economics               Mass-driven deployment cost model.
sensitivity_analysis    Sweeps and trade-space grids.
"""

from __future__ import annotations

__version__ = "0.1.0"

from . import (  # noqa: F401
    coolant,
    constants,
    economics,
    materials,
    orbital_environment,
    physics,
    radiator,
    semiconductors,
    sensitivity_analysis,
    units,
)

__all__ = [
    "constants",
    "units",
    "physics",
    "radiator",
    "coolant",
    "orbital_environment",
    "materials",
    "semiconductors",
    "economics",
    "sensitivity_analysis",
    "__version__",
]
