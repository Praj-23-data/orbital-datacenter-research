# Semiconductor Materials and Thermal Co-Design

This is the scientific heart of the project. The question is blunt: **does raising
the allowable junction temperature reduce orbital radiator mass more than
improving the radiator itself?** The answer, quantitatively, is yes — by a wide
margin — because of the fourth-power law.

## The materials

| Material | Bandgap [eV] | k [W/m/K] | Max Tj [K] | Max Tj [°C] | Rad. tolerance | TRL |
|---|---|---|---|---|---|---|
| Silicon (Si) | 1.12 | 150 | 398 | 125 | moderate | 9 |
| Gallium Nitride (GaN) | 3.40 | 160 | 573 | 300 | high | 7 |
| Silicon Carbide (4H-SiC) | 3.26 | 370 | 623 | 350 | high | 8 |
| Gallium Oxide (β-Ga₂O₃) | 4.80 | 23 | 773 | 500 | high | 4 |
| Diamond | 5.47 | 2200 | 1073 | 800 | very high | 3 |

Wide-bandgap materials tolerate higher junction temperatures because thermally
generated intrinsic carriers (∝ exp(−Eg/2kT)) remain negligible far hotter than
in silicon, so the device still switches cleanly. Diamond additionally has
extraordinary thermal conductivity, easing the junction-to-coolant resistance.

## Why temperature beats emissivity

Radiator area scales as

    A ∝ Q / (ε · (T_rad^4 − T_sink^4))

Two levers appear. Emissivity `ε` is **linear and bounded**: it can only run from
roughly 0.5 to 1.0, a hard ceiling of 2× improvement. Temperature enters as
`T^4`, and the allowable temperature span from silicon (125 °C) to diamond
(800 °C) is enormous. Pushing the radiator from a silicon-limited ~70 °C to a
diamond-limited ~745 °C shrinks area by nearly two orders of magnitude.

## Headline result (100 MW heat load, each material at its own Tj_max)

| Material | Radiator T [°C] | Area [m²] | Mass [t] | Mass vs Si |
|---|---|---|---|---|
| Silicon | 70 | 74 948 | 524.6 | 1.00 |
| GaN | 245 | 14 409 | 100.9 | 0.19 |
| SiC | 295 | 9 967 | 69.8 | 0.13 |
| Ga₂O₃ | 445 | 3 903 | 27.3 | 0.052 |
| Diamond | 745 | 966 | 6.8 | 0.013 |

Silicon → diamond is roughly a **78× reduction in radiator area and mass**.
Diamond's radiator masses about **1.3% of silicon's**. No plausible radiator
technology — droplet, sheet, or metamaterial — comes close to that leverage,
because all of them act on the linear/bounded factors (ε, areal density) rather
than on `T^4`.

Implementation: `simulations/semiconductors.py` (`material_comparison_table`,
`junction_temperature_sweep`, `ThermalBudget`).

## Counter-pressures (why this is not a free win)

- **Leakage** rises with temperature; static power can erode the compute budget
  the hotter design was meant to enable.
- **Reliability**: electromigration and dielectric breakdown accelerate with
  temperature (Arrhenius); high-Tj operation trades mass for lifetime risk.
- **Surrounding electronics**: capacitors, board materials, optics and power
  electronics often cannot run as hot as the wide-bandgap die, capping the loop
  temperature below the die's nominal maximum.
- **Maturity**: diamond and Ga₂O₃ sit at low TRL (3–4); the mass argument is a
  target, not a procurement option today. SiC (TRL 8) is the realistic
  near-term lever and already buys ~7× over silicon.

## References

- Wort & Balmer, "Diamond as an electronic material," *Materials Today* (2008).
- Higashiwaki et al., "Gallium oxide power devices," *Semiconductor Science and
  Technology* (2016).
- Millán et al., "A survey of wide bandgap power semiconductor devices,"
  *IEEE Trans. Power Electronics* (2014).
- Pengelly et al., "A review of GaN on SiC HEMTs," *IEEE Trans. Microwave Theory*
  (2012).

## Limitations

- Maximum junction temperatures are nominal material limits, not qualified
  device ratings.
- Leakage/reliability counter-pressures are discussed but not yet folded into a
  combined objective function.

## Future improvements

- Add an Arrhenius reliability penalty and a leakage-power model to compute a
  true mass-optimal junction temperature rather than the material ceiling.
- Couple to the economics module to express the optimum in $/MW rather than mass.
