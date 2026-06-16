# Literature Review

This review situates the project against existing work in spacecraft thermal
control, advanced radiators, wide-bandgap power electronics, and the emerging
discussion of orbital computing. It is a narrative orientation, not an
exhaustive bibliography; primary references are listed per topic.

## 1. Spacecraft thermal control

The canonical reference is the *Spacecraft Thermal Control Handbook* (Gilmore,
ed.). Conventional spacecraft reject heat through fixed and deployable panel
radiators with high-emittance coatings, sized by the Stefan–Boltzmann law and
operated near room temperature. The state of practice rejects on the order of a
few hundred watts per square metre. A 100 MW–1 GW data center is three to six
orders of magnitude beyond any flown thermal system, which is precisely what
makes radiator mass the central design problem.

## 2. Advanced and low-mass radiators

Three concepts recur in the literature as ways to beat the areal density of
solid panels:

- **Liquid droplet radiators (LDR):** a sheet of fine droplets is sprayed across
  a gap and collected, radiating directly with almost no structural mass. Studied
  extensively by Mattick & Hertzberg (1980s) and by NASA Lewis/Glenn. Key risks
  are droplet loss and collection in microgravity.
- **Liquid sheet / film radiators:** a thin moving film radiates and is
  recovered; lower loss risk than droplets, modest structural mass.
- **Moving-belt and curie-point radiators:** niche, not modelled here.

This repository implements droplet (Model 4) and liquid-sheet (Model 5) radiators
and confirms substantial mass savings over solid panels, while showing they act
on the *linear* (areal density) lever, not the temperature lever.

## 3. Metamaterial / high-emissivity surfaces

Engineered surfaces can push emissivity toward unity and tailor spectral
selectivity. The repository (Model 6) treats emissivity as a variable from 0.5
to 1.0 and demonstrates the hard 2× ceiling this lever implies — useful but
bounded, by construction.

## 4. Wide-bandgap power and high-temperature electronics

A large body of work (Millán et al.; Pengelly et al. on GaN-on-SiC; Higashiwaki
et al. on Ga₂O₃; Wort & Balmer on diamond) establishes that wide-bandgap devices
operate reliably at far higher junction temperatures than silicon. Most of this
literature is motivated by power density and switching efficiency on the ground,
not by radiator mass in space. The novel framing here is to treat the maximum
junction temperature as a *thermal-architecture* variable and quantify its
leverage on orbital mass.

## 5. Orbital data centers

Industry interest in space-based compute has grown (proposals for solar-powered
orbital AI clusters; studies of GW-scale constellations). Public technical
analysis of the *thermal* feasibility at these scales remains thin. This project
contributes an open, reproducible thermal-and-mass framework rather than a point
design.

## Gap this project addresses

Prior art treats radiator technology and semiconductor temperature as separate
disciplines. The contribution here is the explicit **co-design** comparison: a
fourth-power temperature lever versus linear/bounded radiator-technology levers,
evaluated on a common mass and cost basis.

## Selected references

- Gilmore (ed.), *Spacecraft Thermal Control Handbook*, Aerospace Press, 2002.
- Mattick & Hertzberg, "Liquid droplet radiators for heat rejection in space,"
  *J. Energy*, 1981.
- White, "Liquid sheet radiators," NASA technical reports.
- Millán et al., *IEEE Trans. Power Electronics*, 2014.
- Higashiwaki et al., *Semicond. Sci. Technol.*, 2016.
- Wort & Balmer, *Materials Today*, 2008.
- Wertz & Larson, *Space Mission Analysis and Design*, Microcosm.
