# Thermal Architecture for Orbital Data Centers

### A Theoretical Investigation of Heat Rejection Systems for Large-Scale Computing in Vacuum

---

## Abstract

We investigate whether a 100 MW–1 GW orbital AI data center can be thermally
managed in vacuum, where heat rejection occurs only by radiation to deep space.
Using a reproducible, SI-consistent simulation framework, we size radiators,
coolant loops, and structures across radiator technologies, coolants, orbital
regimes, and semiconductor materials. The central finding is that **semiconductor
operating temperature is the dominant lever on radiator mass**: because radiator
area scales as `1/(T⁴ − T_sink⁴)`, raising the allowable junction temperature
from silicon's limit to a diamond-class limit reduces radiator area and mass by
roughly 78×, far exceeding the bounded ≤2× benefit available from emissivity
improvements. Radiator-technology innovations (droplet, liquid-sheet,
metamaterial) deliver real but linear savings on areal density, not the
order-of-magnitude leverage of temperature. We conclude that high-temperature
wide-bandgap electronics are the enabling technology for orbital compute at
scale, with silicon carbide the realistic near-term lever and
diamond/gallium-oxide the long-term target.

---

## 1. Problem statement

In vacuum there is no convection, no evaporative cooling, and no air cooling. The
only exit for waste heat is thermal radiation to the 2.725 K deep-space sink. A
100 MW compute load that degrades essentially all of its electrical power to heat
therefore requires a radiator whose
size is governed entirely by the Stefan–Boltzmann law. The research question is
whether such a system can be made mass-feasible, and which design lever —
radiators, coolants, semiconductor temperature, or materials — matters most.

## 2. Methods

The framework is organised as an importable physics package (`simulations/`) and
seven runnable models (`models/`). Governing equations (Section 3) are
implemented with unit validation and cross-checked symbolically with `sympy`.
Seven Jupyter notebooks reproduce every figure; 29 unit tests pin the physics.

## 3. Governing equations

- Net radiation: `P = n·ε·σ·A·(T⁴ − T_sink⁴)`
- Heat transport: `Q = m_dot·Cp·ΔT`
- Thermal resistance: `R = ΔT/Q`
- Energy balance: `P_in = P_out`
- Solar loading: `P_solar = α·S·A_proj`

See `docs/thermal_physics.md` for derivations and assumptions.

## 4. Results by model

**Baseline (Model 1).** 100 MW, silicon, water, 40 °C coolant, solid panel:
required area ≈ 107,900 m², radiator mass ≈ 755 t, power density ≈ 927 W/m²,
effective efficiency ≈ 0.80. This is the problem to beat.

**High-temperature operation (Model 2).** Raising coolant temperature from 40 °C
to 1000 °C cuts radiator area by ≈273× (area ∝ 1/T⁴). The single most powerful
trend in the study.

**Coolant comparison (Model 3).** Ammonia, lithium, water, molten salt and NaK
ranked by pumping fraction with parallel-channel hydraulics; all stay well below
1% to ~7% of plant power, so coolant choice is a second-order lever set mostly by
temperature range (lithium and molten salt enable high-temperature loops).

**Droplet radiator (Model 4).** At 250 °C with NaK, a droplet radiator reaches
~72× mass reduction versus a solid panel, with negligible evaporative loss
(~10⁻⁵ fraction) — a strong areal-density win.

**Liquid sheet (Model 5).** ~7 t versus ~97 t for an equivalent panel, with film
thickness the main sensitivity — lower loss risk than droplets.

**Metamaterial (Model 6).** Sweeping emissivity 0.5→1.0 yields at most a 2×
area benefit. The lever is real but hard-bounded.

**Semiconductor co-design (Model 7).** Sizing each material at its own maximum
junction temperature (100 MW heat load): silicon 74,948 m²/525 t → diamond
966 m²/6.8 t, a **78× reduction**. Diamond's radiator masses ~1.3% of silicon's.

## 5. The decisive comparison

Emissivity is linear and bounded (`ε ∈ [0.5, 1.0]`, ≤2×). Temperature enters as
the fourth power and ranges over hundreds of kelvin between silicon and diamond.
Therefore temperature dominates every radiator-technology lever by one to two
orders of magnitude. This is the project's headline scientific conclusion.

---

# RESEARCH OUTPUTS

## 1. Executive Summary

Orbital data centers at 100 MW–1 GW are thermally feasible only if radiator mass
is controlled, and the controlling variable is semiconductor operating
temperature, not radiator technology. A silicon, room-temperature baseline needs
a ~108,000 m², ~755 t radiator — likely prohibitive. Moving the same heat load to
high-temperature wide-bandgap electronics shrinks the radiator by up to ~78×.
Radiator innovations (droplet, sheet, metamaterial) help, but linearly and with
hard ceilings. The strategic recommendation is to invest in high-junction-
temperature compute (SiC now, diamond/Ga₂O₃ later) as the enabling technology.

## 2. Technical Findings

- Radiator area ∝ 1/(T⁴ − T_sink⁴); temperature is a fourth-power lever.
- Emissivity is linear and bounded to ≤2× (ε 0.5→1.0).
- Silicon baseline: ~108,000 m², ~755 t at 40 °C / 100 MW.
- Silicon→diamond at each material's Tj_max: ~78× area and mass reduction;
  diamond radiator ≈ 1.3% of silicon's mass.
- Droplet and liquid-sheet radiators give large areal-density savings (~70× and
  ~14× mass vs panel in their cases) with low coolant loss.
- GEO is the kindest environment (~5.5 W/m² absorbed) vs LEO (~208 W/m²).
- Coolant pumping is a minor power penalty (~1–7%); coolant choice matters mainly
  for enabling high-temperature loops (lithium, molten salt).

## 3. Limiting Factors

- **Material maturity:** diamond (TRL 3) and Ga₂O₃ (TRL 4) are not deployable
  today; SiC (TRL 8) is the realistic near-term lever (~7× over silicon).
- **Leakage and reliability:** higher Tj raises static power and accelerates
  wear-out (Arrhenius); the mass-optimal temperature may sit below the material
  ceiling.
- **Peripheral electronics:** capacitors, optics, and power stages may not
  tolerate die-level temperatures, capping loop temperature.
- **Deployment and dynamics:** very large radiators raise structural, attitude-
  control, and micrometeoroid-survivability challenges not modelled here.
- **Power system:** generation and storage mass (and eclipse cycling) are
  significant and only coarsely captured.

## 4. Design Recommendations

1. Treat maximum junction temperature as a first-class architectural variable,
   co-designed with the radiator, not fixed by terrestrial habit.
2. Adopt SiC for the first generation to capture ~7× radiator savings at TRL 8.
3. Fund diamond and Ga₂O₃ device maturation as the highest-leverage long-term
   investment for orbital compute.
4. Pair high-temperature loops with lithium or molten-salt coolants and droplet
   or liquid-sheet radiators to compound areal-density savings on top of the
   temperature win.
5. Prefer GEO where latency permits for the gentlest thermal environment; accept
   LEO's harsher thermal load only when latency/cost dominate.

## 5. Future Research Areas

- A combined objective that folds leakage and Arrhenius reliability into a
  mass-optimal junction temperature in $/MW.
- Two-phase coolant loops and nodal/FEM radiator thermal models.
- Beta-angle-resolved environmental fluxes and eclipse-transient sizing.
- Micrometeoroid/debris survivability of droplet and sheet radiators.
- Bottom-up cost-estimating relationships and lifecycle cost with replacement.

---

## References

See `docs/literature_review.md` and per-module reference sections. Core sources:
Gilmore (ed.) *Spacecraft Thermal Control Handbook*; Mattick & Hertzberg on
droplet radiators; Millán et al., Higashiwaki et al., Wort & Balmer on
wide-bandgap and diamond electronics; Wertz & Larson, *Space Mission Analysis and
Design*.

## Reproducibility

All numbers above are produced by the code in this repository. Run the models in
`models/` or the notebooks in `notebooks/`, or regenerate the summary with
`python generate_research_outputs.py`. Tests: `pytest`.
