# Economics

The economic model (`simulations/economics.py`) converts a thermal architecture
into a deployment cost. It is intentionally simple and transparent: launch mass
times launch price, plus optional hardware cost, expressed per MW of compute and
per kW of heat rejected.

## Mass build-up

    M_total = M_radiator + M_coolant + M_structure + M_power_generation

- **Radiator mass** comes from the sizing models (area × areal density).
- **Coolant mass** is the loop inventory (default 5000 kg placeholder).
- **Structure mass** is the bus/structure allocation (default 20 000 kg).
- **Power-generation mass** = compute power / specific power (default 150 W/kg
  for space photovoltaics).

## Cost

    Cost_launch = M_total · c_launch
    Cost_total  = Cost_launch (+ optional hardware cost/kg)
    Cost_per_MW       = Cost_total / P_compute_MW
    Cost_per_kW_rejected = Cost_total / Q_reject_kW

Default launch price is 500 USD/kg (near-term Starship-class). Reference points
provided for sweeps: Falcon 9 ≈ 2700, Falcon Heavy ≈ 1500, Starship target ≈ 100
USD/kg.

## Why the semiconductor result dominates economics too

Because radiator mass falls ~78× from silicon to diamond, and radiator mass is a
large share of `M_total` at the silicon baseline, the launch-cost lever from
junction temperature dwarfs the lever from launch-price reductions for the
radiator subsystem. `simulations/sensitivity_analysis.py` builds a 2-D
junction-temperature × launch-cost grid that makes this explicit: moving up the
temperature axis saves more than moving down the price axis over realistic
ranges.

## Sensitivity hooks

- `one_dimensional_sweep` — any single parameter vs cost/mass.
- `junction_vs_launchcost_grid` — the headline 2-D trade space.
- `emissivity_vs_temperature_grid` — confirms emissivity is the weaker lever.

## References

- FAA/industry launch-price surveys; SpaceX published figures for Falcon and
  Starship targets.
- Wertz & Larson, *Space Mission Analysis and Design* (mass/cost estimating).

## Limitations

- Hardware (non-launch) cost is a coarse per-kg input, not a bottom-up BOM.
- No operations, insurance, or financing costs.
- Coolant and structure masses are allocations, not sized from first principles.

## Future improvements

- Bottom-up cost estimating relationships per subsystem.
- Monte-Carlo cost uncertainty rather than point estimates.
- Lifecycle cost including replacement launches over mission life.
