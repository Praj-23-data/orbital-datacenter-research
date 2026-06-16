"""Lightweight SI unit validation.

This project deliberately avoids heavyweight unit libraries to keep the
dependency surface small (numpy / scipy / pandas / pydantic only). Instead we
provide:

* :func:`require_positive`, :func:`require_temperature`, etc. -- guard clauses
  that raise informative ``ValueError`` exceptions on physically impossible
  inputs (negative absolute temperature, negative area, emissivity > 1 ...).
* :class:`SIQuantity` -- a tiny dataclass that pairs a float value with a unit
  string so that intermediate results can be self-describing in logs and
  notebooks without changing the numerical type.

The philosophy: validation is *cheap* and prevents the silent
garbage-in/garbage-out failures that plague engineering scripts. Every public
physics function in this package validates its inputs through these helpers.
"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import ABS_ZERO_CELSIUS


# --------------------------------------------------------------------------
# Guard clauses
# --------------------------------------------------------------------------
def require_positive(value: float, name: str) -> float:
    """Return ``value`` if strictly positive, else raise ``ValueError``."""
    if value <= 0:
        raise ValueError(f"{name} must be > 0 (got {value!r}).")
    return float(value)


def require_non_negative(value: float, name: str) -> float:
    """Return ``value`` if >= 0, else raise ``ValueError``."""
    if value < 0:
        raise ValueError(f"{name} must be >= 0 (got {value!r}).")
    return float(value)


def require_temperature_kelvin(value: float, name: str = "temperature") -> float:
    """Validate an absolute temperature in kelvin (must be > 0 K)."""
    if value <= 0:
        raise ValueError(
            f"{name} must be a positive absolute temperature in kelvin "
            f"(got {value!r} K, which is at or below absolute zero)."
        )
    return float(value)


def require_fraction(value: float, name: str) -> float:
    """Validate a dimensionless quantity in the closed interval [0, 1]."""
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{name} must lie in [0, 1] (got {value!r}).")
    return float(value)


# --------------------------------------------------------------------------
# Temperature conversions (single source of truth)
# --------------------------------------------------------------------------
def celsius_to_kelvin(t_celsius: float) -> float:
    """Convert degrees Celsius to kelvin, validating against absolute zero."""
    if t_celsius < ABS_ZERO_CELSIUS:
        raise ValueError(
            f"{t_celsius} C is below absolute zero ({ABS_ZERO_CELSIUS} C)."
        )
    return t_celsius - ABS_ZERO_CELSIUS


def kelvin_to_celsius(t_kelvin: float) -> float:
    """Convert kelvin to degrees Celsius."""
    require_temperature_kelvin(t_kelvin)
    return t_kelvin + ABS_ZERO_CELSIUS


# --------------------------------------------------------------------------
# Self-describing quantity
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class SIQuantity:
    """A value paired with its SI unit string.

    This is intentionally minimal -- it does **not** perform dimensional
    algebra. Its job is to make results legible (``SIQuantity(1234.5, 'm^2')``)
    when they flow into dataframes, logs, or notebook displays.
    """

    value: float
    unit: str

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.value:.6g} {self.unit}"


__all__ = [
    "require_positive",
    "require_non_negative",
    "require_temperature_kelvin",
    "require_fraction",
    "celsius_to_kelvin",
    "kelvin_to_celsius",
    "SIQuantity",
]
