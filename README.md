# Thermal Architecture for Orbital Data Centers

**A theoretical investigation of heat rejection systems for large-scale computing in vacuum.**

In space there is no air, no water spray, no convection — the only way to shed
waste heat is to radiate it to deep space. This repository asks whether a
100 MW–1 GW orbital AI data center can be thermally managed under that
constraint, and which design lever matters most: radiators, coolants,
semiconductor operating temperature, or materials.

**Headline finding:** semiconductor operating temperature dominates. Because
radiator area scales as `1 / (T⁴ − T_sink⁴)`, moving from silicon's temperature
limit to a diamond-class limit shrinks radiator area and mass by about **78×** —
far more than the bounded ≤2× available from better emissivity. High-temperature
wide-bandgap electronics, not exotic radiators, are the enabling technology.

## Repository layout

```
orbital-datacenter-research/
├── README.md
├── RESULTS.md                    # auto-generated research outputs
├── generate_research_outputs.py  # regenerates RESULTS.md + figures/
├── docs/                         # research paper + per-topic documentation
├── simulations/                  # importable physics package
│   ├── constants.py  units.py  physics.py
│   ├── radiator.py   coolant.py  materials.py
│   ├── orbital_environment.py    semiconductors.py
│   ├── economics.py  sensitivity_analysis.py
├── models/                       # 7 runnable model drivers
│   ├── baseline_model/  high_temperature_model/  liquid_metal_model/
│   ├── droplet_radiator_model/  liquid_sheet_model/  metamaterial_model/
│   └── future_chip_model/
├── notebooks/                    # 7 reproducible notebooks (+ builder)
├── tests/                        # pytest suite (29 tests)
├── requirements.txt  pyproject.toml  LICENSE  .gitignore
└── .github/workflows/ci.yml
```

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .          # makes `simulations` and `models` importable
```

## Run

```bash
# A single model driver
python -m models.baseline_model.run
python -m models.future_chip_model.run

# Regenerate the research outputs and publication figures
python generate_research_outputs.py    # writes RESULTS.md and figures/

# The notebooks
jupyter notebook notebooks/

# Tests
pytest
```

## The seven models

1. **Baseline** — 100 MW, silicon, water, 40 °C, solid panel. ~108,000 m², ~755 t.
2. **High-temperature operation** — coolant 40→1000 °C; area falls ≈273×.
3. **Coolant comparison** — water, ammonia, NaK, lithium, molten salt; pumping
   and temperature limits; ranking tables.
4. **Droplet radiator** — residence time, effective area, evaporative loss; large
   areal-density savings.
5. **Liquid sheet radiator** — film thickness sensitivity; low loss risk.
6. **Metamaterial radiator** — emissivity 0.5→1.0; demonstrates the hard 2× ceiling.
7. **Semiconductor co-design** — Si, SiC, GaN, Ga₂O₃, diamond; the ~78× result.

## Key result

| Material | Max Tj | Radiator area | Radiator mass | vs silicon |
|---|---|---|---|---|
| Silicon | 125 °C | 74,948 m² | 525 t | 1.00 |
| GaN | 300 °C | 14,409 m² | 101 t | 0.19 |
| SiC | 350 °C | 9,967 m² | 70 t | 0.13 |
| Ga₂O₃ | 500 °C | 3,903 m² | 27 t | 0.052 |
| Diamond | 800 °C | 966 m² | 6.8 t | 0.013 |

*(100 MW heat load, each material sized at its own maximum junction temperature.)*

## Physics

All models use SI units with validation and a `sympy` symbolic cross-check of the
core relations. Governing equations: Stefan–Boltzmann radiation, `Q = m_dot·Cp·ΔT`
heat transport, `R = ΔT/Q` thermal resistance, energy balance, and solar loading.
See [`docs/thermal_physics.md`](docs/thermal_physics.md) and
[`docs/assumptions.md`](docs/assumptions.md).

## Documentation

- [`docs/research_paper.md`](docs/research_paper.md) — full write-up + research outputs
- [`docs/literature_review.md`](docs/literature_review.md)
- [`docs/thermal_physics.md`](docs/thermal_physics.md)
- [`docs/semiconductor_materials.md`](docs/semiconductor_materials.md)
- [`docs/orbital_environment.md`](docs/orbital_environment.md)
- [`docs/economics.md`](docs/economics.md)
- [`docs/assumptions.md`](docs/assumptions.md)

## Limitations

Steady-state, grey-body, isothermal-panel modelling; coarse coolant/structure mass
allocations; no debris erosion, attitude, or lifecycle degradation. Each module's
docstring and the research paper detail these and the planned extensions.
