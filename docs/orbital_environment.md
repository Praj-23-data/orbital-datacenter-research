# Orbital Environment

The radiator's effective sink temperature, and the parasitic heat it absorbs,
depend on where the data center flies. This module (`simulations/orbital_environment.py`)
models three regimes and the heat fluxes each imposes.

## Regimes

| Regime | Altitude | Earth view factor | Orbital period | Eclipse fraction |
|---|---|---|---|---|
| LEO | 500 km | large | ~94 min | ~0.38 |
| MEO | 20 200 km | small | ~718 min | ~0.08 |
| GEO | 35 786 km | very small | ~1436 min | ~0.05 |

View factor uses `(R_earth / r)²`; eclipse fraction uses the geometric
`arcsin(R_earth/r)/π`; period is Keplerian, `2π·sqrt(r³/μ)`.

## Environmental fluxes (edge-on radiator)

Absorbed flux on a radiator oriented edge-on to the sun, by regime:

| Regime | Solar | Albedo | Earth IR | Total absorbed |
|---|---|---|---|---|
| LEO | 0 | 35.1 | 173.2 | **208.3 W/m²** |
| MEO | 0 | 2.3 | 11.6 | 13.9 W/m² |
| GEO | 0 | 0.9 | 4.6 | **5.5 W/m²** |

The direct solar term is zero in the edge-on idealisation; the residual load is
albedo + planetary IR, which falls off steeply with altitude through the view
factor. **GEO is by far the kindest thermal environment**: a radiator there
absorbs ~38× less parasitic flux than in LEO, so more of its `εσT⁴` capability
goes to rejecting computer heat rather than fighting the Earth.

## Trade-offs beyond thermal

- **LEO** is harshest thermally and has frequent eclipses, but offers the lowest
  launch cost per kg and the lowest communication latency to the ground.
- **GEO** is thermally kindest and nearly eclipse-free, but is the most
  expensive to reach and has high latency.
- **MEO** is an intermediate compromise.

Eclipse periods matter for the *power* system (batteries/storage) more than for
the radiator: during eclipse the parasitic solar/albedo load vanishes, so the
radiator is briefly over-sized rather than under-sized.

## Deep-space orientation

The model assumes the radiator can be pointed edge-on to the sun and broadside
to deep space. Real attitude constraints (antenna pointing, solar-array
tracking) will compromise this; the absorbed-flux numbers above are therefore a
best case, and `radiator_area()` accepts an `absorbed_flux` penalty to explore
worse orientations.

## References

- Gilmore (ed.), *Spacecraft Thermal Control Handbook*.
- Vallado, *Fundamentals of Astrodynamics and Applications* (orbital geometry).
- NASA Earth radiation budget data for albedo/IR baselines.

## Limitations

- Albedo and Earth-IR are treated as orbit-averaged scalars, not
  latitude/beta-angle dependent fields.
- No seasonal or diurnal variation of Earth IR.

## Future improvements

- Beta-angle-resolved flux integration over an orbit.
- Coupled eclipse-transient radiator and storage sizing.
