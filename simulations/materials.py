"""Radiator structural materials and optical coatings.

Two databases:

* :data:`STRUCTURAL_MATERIALS` -- candidate radiator panel/fin materials with
  density, thermal conductivity, and a representative areal density when built
  into a deployable radiator. Used to translate radiating *area* into *mass*.
* :data:`COATINGS` -- optical coatings characterised by solar absorptance
  ``alpha`` and infrared emissivity ``epsilon``. The ratio ``alpha/epsilon``
  governs equilibrium temperature under sunlight; radiators want low alpha and
  high epsilon.

Fin efficiency
--------------
Real radiators are not isothermal: heat conducts from the coolant tube out
along the fin and the fin tip runs cooler, radiating less. :func:`fin_efficiency`
implements the classic straight-fin radiating efficiency so that radiator
sizing can include this real loss instead of assuming a perfectly isothermal
panel.

References
----------
[1] Gilmore, D. (2002) *Spacecraft Thermal Control Handbook*, AIAA, ch. 4 & 6.
[2] Incropera & DeWitt, *Fundamentals of Heat and Mass Transfer*, fins chapter.
[3] Henninger, J.H. (1984) "Solar Absorptance and Thermal Emittance of Some
    Common Spacecraft Thermal-Control Coatings", NASA RP-1121.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .constants import STEFAN_BOLTZMANN
from .units import require_fraction, require_positive


@dataclass(frozen=True)
class StructuralMaterial:
    name: str
    density_kg_m3: float
    thermal_conductivity_w_m_k: float
    max_service_temp_k: float
    representative_areal_density_kg_m2: float
    note: str = ""


STRUCTURAL_MATERIALS: dict[str, StructuralMaterial] = {
    "aluminum": StructuralMaterial(
        "Aluminum 6061", 2700.0, 167.0, 600.0, 7.0,
        "Conventional baseline radiator material.",
    ),
    "titanium": StructuralMaterial(
        "Titanium Ti-6Al-4V", 4430.0, 6.7, 870.0, 9.0,
        "High-temperature loops; poor conductivity needs heat pipes.",
    ),
    "copper": StructuralMaterial(
        "Copper", 8960.0, 401.0, 900.0, 14.0,
        "Excellent conductivity, heavy; good for high-flux spreaders.",
    ),
    "graphite_composite": StructuralMaterial(
        "Graphite-epoxy / k-core", 1800.0, 300.0, 450.0, 3.5,
        "High-conductivity, low-density advanced panel.",
    ),
    "carbon_carbon": StructuralMaterial(
        "Carbon-carbon", 1900.0, 250.0, 2200.0, 4.0,
        "Extreme-temperature capable advanced radiator.",
    ),
}


@dataclass(frozen=True)
class Coating:
    name: str
    solar_absorptance: float
    ir_emittance: float
    note: str = ""

    @property
    def alpha_over_epsilon(self) -> float:
        return self.solar_absorptance / self.ir_emittance


COATINGS: dict[str, Coating] = {
    "silvered_teflon": Coating("Silvered Teflon (Ag/FEP)", 0.08, 0.78,
                               "Classic low-alpha radiator coating."),
    "white_paint_z93": Coating("White paint Z93", 0.17, 0.92,
                               "Durable white thermal-control paint."),
    "osr": Coating("Optical Solar Reflector (quartz mirror)", 0.07, 0.80,
                   "Lowest alpha/epsilon; rigid second-surface mirror."),
    "black_paint": Coating("Black paint (Chemglaze Z306)", 0.95, 0.90,
                           "High alpha; only for shaded radiators."),
    "metamaterial_ideal": Coating("Engineered metamaterial (ideal)", 0.05, 0.99,
                                  "Aspirational selective emitter, epsilon->1."),
}


def fin_efficiency(
    fin_length_m: float,
    fin_thickness_m: float,
    conductivity_w_m_k: float,
    emissivity: float,
    base_temperature_k: float,
) -> float:
    """Radiating straight-fin efficiency (0-1).

    Uses the linearized radiating-fin parameter

    .. math::
        m = \\sqrt{\\frac{2\\,\\varepsilon\\,\\sigma\\,T_b^3}{k\\,t}}

    and ``eta = tanh(mL)/(mL)``. This captures the temperature droop along the
    fin and therefore the *effective* emitting capability versus an ideal
    isothermal panel. A useful sanity bound on real radiator performance.
    """
    require_positive(fin_length_m, "fin_length_m")
    require_positive(fin_thickness_m, "fin_thickness_m")
    require_positive(conductivity_w_m_k, "conductivity_w_m_k")
    require_fraction(emissivity, "emissivity")
    require_positive(base_temperature_k, "base_temperature_k")
    m = np.sqrt(
        2.0 * emissivity * STEFAN_BOLTZMANN * base_temperature_k**3
        / (conductivity_w_m_k * fin_thickness_m)
    )
    ml = m * fin_length_m
    return float(np.tanh(ml) / ml)


__all__ = [
    "StructuralMaterial",
    "STRUCTURAL_MATERIALS",
    "Coating",
    "COATINGS",
    "fin_efficiency",
]
