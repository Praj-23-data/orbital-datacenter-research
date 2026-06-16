"""Build all project notebooks programmatically with nbformat.

Run from the repository root:

    python notebooks/build_notebooks.py

This regenerates the seven analysis notebooks as valid .ipynb files. Keeping
the notebook *source* in a Python builder makes them diff-friendly and
guarantees they stay in sync with the simulation API.
"""

from __future__ import annotations

import os

import nbformat as nbf
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = os.path.dirname(os.path.abspath(__file__))

PREAMBLE = (
    "import sys, os\n"
    "sys.path.insert(0, os.path.abspath('..'))\n"
    "import numpy as np, pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "plt.rcParams.update({'figure.dpi': 110, 'font.size': 11})\n"
)


def _save(nb: nbf.NotebookNode, name: str) -> None:
    path = os.path.join(HERE, name)
    with open(path, "w") as f:
        nbf.write(nb, f)
    print("wrote", path)


def nb01() -> None:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# 01 - Baseline Orbital Data Centre\n"
            "100 MW, silicon, water cooling at 40 C, traditional panel radiator. "
            "Establishes the reference radiator area and mass."
        ),
        new_code_cell(PREAMBLE + "from models.baseline_model.run import run\n"
                      "res = run()\npd.Series(res)"),
        new_code_cell(
            "labels = ['area_m2','mass_kg']\n"
            "print(f\"Radiator area : {res['radiator_area_m2']:.0f} m^2\")\n"
            "print(f\"Radiator mass : {res['radiator_mass_tonnes']:.1f} t\")\n"
            "print(f\"Power density : {res['power_density_w_per_m2']:.0f} W/m^2\")"
        ),
    ]
    _save(nb, "01_baseline.ipynb")


def nb02() -> None:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# 02 - Coolant Temperature Sweep\n"
            "Radiator area and mass collapse as ~T^-4 when coolant temperature "
            "rises from 40 C to 1000 C."
        ),
        new_code_cell(PREAMBLE + "from models.high_temperature_model.run import run\n"
                      "df = run(); df"),
        new_code_cell(
            "fig, ax = plt.subplots(1,2, figsize=(11,4))\n"
            "ax[0].plot(df['coolant_C'], df['area_m2']/1e3, 'o-')\n"
            "ax[0].set_xlabel('Coolant T [C]'); ax[0].set_ylabel('Area [1000 m^2]')\n"
            "ax[0].set_title('Radiator area vs temperature')\n"
            "ax[1].plot(df['coolant_C'], df['mass_reduction_x'], 's-', color='crimson')\n"
            "ax[1].set_xlabel('Coolant T [C]'); ax[1].set_ylabel('Mass reduction (x)')\n"
            "ax[1].set_title('Mass reduction vs 40 C baseline')\n"
            "plt.tight_layout(); plt.show()"
        ),
    ]
    _save(nb, "02_temperature_sweep.ipynb")


def nb03() -> None:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# 03 - Radiator Area & Advanced Concepts\n"
            "Compares panel, droplet and liquid-sheet radiators and the bounded "
            "benefit of emissivity (metamaterial) engineering."
        ),
        new_code_cell(PREAMBLE +
                      "from models.droplet_radiator_model.run import run as drun\n"
                      "from models.liquid_sheet_model.run import run as srun\n"
                      "from models.metamaterial_model.run import run as mrun\n"
                      "d = drun(); s = srun(); m = mrun()\n"
                      "print('droplet mass reduction x:', round(d['mass_reduction_vs_panel_x'],1))"),
        new_code_cell(
            "fig, ax = plt.subplots(figsize=(7,4))\n"
            "ax.plot(m['emissivity'], m['area_m2']/1e3, 'o-')\n"
            "ax.set_xlabel('Emissivity'); ax.set_ylabel('Area [1000 m^2]')\n"
            "ax.set_title('Emissivity sweep (bounded <=2x benefit)')\n"
            "plt.tight_layout(); plt.show()"
        ),
    ]
    _save(nb, "03_radiator_area.ipynb")


def nb04() -> None:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# 04 - Mass Analysis\n"
            "Radiator mass across radiator technologies at a common 250 C "
            "operating point."
        ),
        new_code_cell(PREAMBLE +
                      "from models.droplet_radiator_model.run import run as drun\n"
                      "from models.liquid_sheet_model.run import run as srun\n"
                      "d = drun(); s = srun()\n"
                      "masses = {'Panel': d['panel_mass_kg'], 'Liquid sheet': s['sensitivity']['total_mass_kg'].min(), 'Droplet': d['droplet_mass_kg']}\n"
                      "pd.Series(masses, name='mass_kg')"),
        new_code_cell(
            "ser = pd.Series({'Panel': d['panel_mass_kg'], 'Liquid sheet': s['sensitivity']['total_mass_kg'].min(), 'Droplet': d['droplet_mass_kg']})\n"
            "ax = (ser/1e3).plot.bar(color=['steelblue','seagreen','indianred'])\n"
            "ax.set_ylabel('Mass [t]'); ax.set_title('Radiator mass by concept @250 C')\n"
            "plt.tight_layout(); plt.show()"
        ),
    ]
    _save(nb, "04_mass_analysis.ipynb")


def nb05() -> None:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# 05 - Orbital Economics\n"
            "Deployment cost vs junction temperature and launch cost per kg."
        ),
        new_code_cell(PREAMBLE +
                      "from simulations.sensitivity_analysis import junction_vs_launchcost_grid\n"
                      "tj = np.linspace(400, 1080, 25)\n"
                      "lc = np.array([100, 300, 500, 1500, 2700])\n"
                      "grid = junction_vs_launchcost_grid(100e6, 100e6, tj, lc)\n"
                      "grid.head()"),
        new_code_cell(
            "pivot = grid.pivot(index='junction_temp_k', columns='launch_cost_usd_per_kg', values='cost_per_mw_usd')\n"
            "fig, ax = plt.subplots(figsize=(7,5))\n"
            "im = ax.imshow(pivot.values/1e6, aspect='auto', origin='lower',\n"
            "               extent=[lc.min(), lc.max(), tj.min(), tj.max()], cmap='viridis')\n"
            "ax.set_xlabel('Launch cost [$/kg]'); ax.set_ylabel('Junction T [K]')\n"
            "ax.set_title('Cost per MW [$M]'); fig.colorbar(im, label='$M / MW')\n"
            "plt.tight_layout(); plt.show()"
        ),
    ]
    _save(nb, "05_orbital_economics.ipynb")


def nb06() -> None:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# 06 - Material Comparison\n"
            "Coolants and semiconductors side by side."
        ),
        new_code_cell(PREAMBLE +
                      "from simulations.coolant import coolant_ranking_table\n"
                      "from simulations.semiconductors import material_comparison_table\n"
                      "coolant_ranking_table(100e6, 20.0)"),
        new_code_cell("material_comparison_table(100e6)"),
    ]
    _save(nb, "06_material_comparison.ipynb")


def nb07() -> None:
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(
            "# 07 - Semiconductor Temperature Scaling (central result)\n"
            "Junction temperature vs radiator area, mass, launch mass and launch "
            "cost. The T^-4 collapse dwarfs the bounded emissivity benefit."
        ),
        new_code_cell(PREAMBLE +
                      "from models.future_chip_model.run import run\n"
                      "out = run(); sweep = out['sweep']; sweep.head()"),
        new_code_cell(
            "fig, ax = plt.subplots(2,2, figsize=(11,8))\n"
            "ax[0,0].plot(sweep['junction_temp_k'], sweep['radiator_area_m2']/1e3); ax[0,0].set_title('Area [1000 m^2]')\n"
            "ax[0,1].plot(sweep['junction_temp_k'], sweep['radiator_mass_kg']/1e3); ax[0,1].set_title('Radiator mass [t]')\n"
            "ax[1,0].plot(sweep['junction_temp_k'], sweep['total_mass_kg']/1e3); ax[1,0].set_title('Total launch mass [t]')\n"
            "ax[1,1].plot(sweep['junction_temp_k'], sweep['deployment_cost_usd']/1e9); ax[1,1].set_title('Deployment cost [$B]')\n"
            "for a in ax.flat: a.set_xlabel('Junction T [K]')\n"
            "plt.tight_layout(); plt.show()"
        ),
        new_code_cell("out['material_table']"),
    ]
    _save(nb, "07_semiconductor_temperature_scaling.ipynb")


if __name__ == "__main__":
    nb01(); nb02(); nb03(); nb04(); nb05(); nb06(); nb07()
    print("All notebooks built.")
