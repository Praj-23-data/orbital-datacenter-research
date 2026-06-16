"""Shared, validated configuration for all model drivers.

Centralises the baseline assumptions (power level, thermal budget, launch cost)
as a pydantic model so every driver starts from the same, validated numbers and
sensitivity studies can override single fields cleanly.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class BaseConfig(BaseModel):
    """Validated baseline assumptions shared across models (SI units)."""

    compute_power_w: float = Field(100e6, description="Electrical compute power, W")
    heat_fraction: float = Field(
        1.0, ge=0.0, le=1.0,
        description="Fraction of compute power that becomes waste heat (~1.0).",
    )
    emissivity: float = Field(0.85, ge=0.0, le=1.0)
    areal_density_kg_m2: float = Field(7.0, gt=0.0)
    radiating_sides: int = Field(2)
    launch_cost_usd_per_kg: float = Field(500.0, gt=0.0)

    # junction-to-radiator temperature budget (K)
    junction_to_coolant_k: float = Field(25.0, ge=0.0)
    coolant_rise_k: float = Field(20.0, ge=0.0)
    coolant_to_radiator_k: float = Field(10.0, ge=0.0)

    # auxiliary masses (kg)
    coolant_kg: float = Field(5000.0, ge=0.0)
    structure_kg: float = Field(20000.0, ge=0.0)
    pv_specific_power_w_per_kg: float = Field(150.0, gt=0.0)

    @field_validator("radiating_sides")
    @classmethod
    def _sides(cls, v: int) -> int:
        if v not in (1, 2):
            raise ValueError("radiating_sides must be 1 or 2")
        return v

    @property
    def heat_to_reject_w(self) -> float:
        return self.compute_power_w * self.heat_fraction


DEFAULT_CONFIG = BaseConfig()
