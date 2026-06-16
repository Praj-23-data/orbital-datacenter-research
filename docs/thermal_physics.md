# Thermal Physics

This document defines the governing equations used throughout the repository and
the assumptions behind each. All quantities are SI unless explicitly stated. The
canonical implementation lives in `simulations/physics.py`, with symbolic
cross-checks built in `sympy`.

## 1. The central constraint: radiation is the only exit

In a vacuum there is no working fluid in contact with the radiator's outer
surface, so convection and evaporation to the environment are unavailable. The
only mechanism that moves heat from the spacecraft to the universe is
electromagnetic radiation to the deep-space sink (the cosmic microwave
background at `T_sink = 2.725 K`). Every architectural decision in this project
flows from that single fact.

## 2. Stefan–Boltzmann radiation

The net power radiated by a grey surface of area `A`, emissivity `ε`, at uniform
temperature `T`, against a sink at `T_sink` is

    P = n · ε · σ · A · (T^4 − T_sink^4)

where `σ = 5.670374419e-8 W m^-2 K^-4` and `n` is the number of radiating faces
(`n = 2` for a thin double-sided panel, `n = 1` if one face is blocked or
insulated). Because `T_sink^4 ≈ 55 K^4` is negligible against any practical
radiator temperature (e.g. `313 K → 9.6e9 K^4`), the sink term is small but is
retained for correctness rather than dropped.

The fourth-power dependence is the most important single feature of the whole
problem. Doubling the radiator temperature cuts the required area by a factor of
sixteen. This is why semiconductor operating temperature (Model 7) turns out to
dominate radiator technology.

`radiator_area()` inverts this relation to solve for area given a heat load, and
raises `ValueError` when an environmental flux makes the load physically
impossible to reject at the requested temperature (absorbed flux ≥ gross
emissive capability).

## 3. Heat transport in the coolant loop

Heat must be carried from the chips to the radiator by a circulating coolant:

    Q = m_dot · Cp · ΔT

with mass flow `m_dot` [kg/s], specific heat `Cp` [J/kg/K], and the temperature
rise `ΔT` across the load. Inverting gives the mass flow a given duty requires,
which in turn sets pumping power (see `coolant.py`).

## 4. Thermal resistance network

Each interface between junction and radiating surface adds a resistance:

    R = ΔT / Q          (general)
    R_cond = L / (k · A) (conduction through a slab)

Resistances in series add. The junction-to-coolant, coolant-rise, and
coolant-to-radiator budget (Model 7) is a three-resistance chain that sets how
far the radiator temperature sits below the junction temperature.

## 5. Energy balance

At steady state, power in equals power out:

    P_in = P_out  ⇒  Q_chips + Q_absorbed_environment = P_radiated

`energy_balance_residual()` returns the signed mismatch and `is_balanced()`
checks it against a tolerance. Notebooks use these to confirm that every sized
radiator actually closes its own energy budget.

## 6. Solar and environmental loading

A radiator does not see only deep space; it also absorbs sunlight, albedo, and
planetary infrared:

    P_solar = α · S · A_projected

with solar absorptance `α`, solar constant `S = 1361 W/m^2`, and the projected
(not total) area facing the sun. Earth-IR absorption is governed by the IR
emittance via Kirchhoff's law. These loads are treated as a penalty that
subtracts from the radiator's gross capability in `radiator_area()` and are
quantified per orbit in `orbital_environment.py`.

## References

- Incropera & DeWitt, *Fundamentals of Heat and Mass Transfer*.
- Gilmore (ed.), *Spacecraft Thermal Control Handbook*, Aerospace Press.
- Modest, *Radiative Heat Transfer*.
- Siegel & Howell, *Thermal Radiation Heat Transfer*.

## Limitations

- Radiators are treated as isothermal at the panel level; real fin gradients are
  captured only through a separate fin-efficiency factor, not a full 2-D solve.
- Grey-body emissivity is assumed wavelength-independent.
- View factors to the spacecraft body and self-illumination between panels are
  not modelled.

## Future improvements

- Replace the lumped panel with a nodal/FEM thermal network.
- Spectral (non-grey) emissivity for metamaterial surfaces.
- Transient eclipse response rather than steady-state averages.
