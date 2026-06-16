# Assumptions and Scope

This file collects every material assumption in one place so that results can be
reproduced and critiqued. Numbers in brackets are the repository defaults
(`models/config.py`, `DEFAULT_CONFIG`).

## System-level

- Total IT/compute power: 100 MW baseline (the framework scales to 1 GW).
- Fraction of electrical power that becomes heat to reject: 1.0 by default
  (`heat_fraction = 1.0`), i.e. essentially all electrical power degrades to heat
  and must be radiated. A more optimistic accounting can set this to ~0.80 to
  deduct power-conversion losses radiated elsewhere; the framework exposes it as
  a single config knob so the user can run either convention.
- Steady-state operation. Eclipse transients are characterised separately in
  the orbital module but the sizing models use steady-state averages.

## Radiator

- Default emissivity ε = 0.85 (high-emittance coating such as white paint Z93 or
  silvered Teflon).
- Default areal density 7 kg/m² for a deployable double-sided panel including
  fluid, manifolds, and structure. This is deliberately mid-range; aggressive
  designs reach 3–5 kg/m², heritage hardware is heavier.
- Two radiating faces unless a model states otherwise.
- Radiator oriented edge-on to the sun where possible, so direct solar load is
  minimised and the dominant environmental term is planetary IR + albedo.

## Coolant

- Single-phase sensible-heat transport (Q = m_dot·Cp·ΔT). Two-phase loops are
  noted as future work.
- Parallel-channel hydraulics sized to a target bulk velocity (default 3 m/s,
  channel diameter 0.02 m) so pumping power is physical. A naive single-pipe
  model produces non-physical (supersonic) velocities at 100 MW and is rejected.

## Semiconductor

- Each material is allowed to run up to its own maximum junction temperature.
- A fixed thermal budget separates junction from radiator: junction-to-coolant
  25 K, coolant rise 20 K, coolant-to-radiator 10 K (55 K total by default).
- Radiation tolerance and TRL are qualitative tags used for ranking, not inputs
  to the thermal solve.

## Orbital environment

- Solar constant 1361 W/m², Earth albedo 0.30, Earth IR 237 W/m² at the surface,
  scaled by view factor (R_earth/r)².
- Three regimes: LEO (500 km), MEO (20 200 km), GEO (35 786 km).
- Deep-space sink at 2.725 K.

## Economics

- Launch cost default 500 USD/kg (Starship-class near-term). Falcon 9/Heavy and
  a 100 USD/kg aspirational target are provided for sweeps.
- Power-generation mass from specific power 150 W/kg (current space PV).

## What is deliberately NOT modelled

- Micrometeoroid and debris erosion of radiators and droplet streams.
- Attitude-control propellant and pointing budgets.
- Data-link and ground-segment economics.
- Degradation over mission life (coating darkening, PV decay).

These omissions are revisited in each module's "Future improvements" section and
in `docs/research_paper.md` under Limiting Factors.
