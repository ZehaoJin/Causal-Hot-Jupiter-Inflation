# Causal Hot Jupiter Inflation

<p align="center">
  <img src="docs/hot_jupiter_causal_cartoon.svg" alt="Illustration of a star irradiating an inflated hot Jupiter." width="900">
</p>

Code, data, and manuscript files for paper "Causes of Hot Jupiter Inflation from Causal Discovery" [docs/Exoplanets_v2.pdf](docs/Exoplanets_v2.pdf).

## Menu

- [Files](#files)
- [Requirements](#requirements)
- [Reproduce the paper setup](#reproduce-the-paper-setup)
- [Age-extended run](#age-extended-run)
- [Super-Earth sanity check](#super-earth-sanity-check)
- [Use your own dataset](#use-your-own-dataset)
- [Cite this work](#cite-this-work)

## Files

- [docs/Exoplanets_v2.pdf](docs/Exoplanets_v2.pdf) — paper
- [docs/hot_jupiter_causal_cartoon.svg](docs/hot_jupiter_causal_cartoon.svg) — README illustration
- [data/hot_jupiters_20260403.csv](data/hot_jupiters_20260403.csv) — main hot-Jupiter sample
- [data/hot_jupiters_20260714_age.csv](data/hot_jupiters_20260714_age.csv) — age-extended sample
- [data/20260526_SE_SN.csv](data/20260526_SE_SN.csv) — Super-Earth sanity-check dataset
- [src/run_tetrad_boss_star_teff_prior.py](src/run_tetrad_boss_star_teff_prior.py) — Tetrad BOSS runner

## Requirements

```bash
python -m pip install pandas pydot pytetrad
export JAVA_HOME=/path/to/your/jdk
```

Also install **Graphviz** so `pydot` can write `.png` and `.pdf` graphs.

## Reproduce the paper setup

From `/home/runner/work/Causal-Hot-Jupiter-Inflation/Causal-Hot-Jupiter-Inflation`:

```bash
python src/run_tetrad_boss_star_teff_prior.py
```

The default run matches the paper setup:

- dataset: [data/hot_jupiters_20260403.csv](data/hot_jupiters_20260403.csv)
- score: `ffml`
- prior: planet properties do not cause host-star properties
  - `mass`, `radius`, and `orbital_period` cannot cause `star_teff`
  - in the age-extended run, `star_age` is also treated as a host-star-side cause
- outputs: `results/tetrad_boss_star_teff_not_child/`

Main result from the paper: `R_p` has direct parents `P_orb` and `T_eff`, while no direct `M_p -> R_p` edge is recovered.

## Age-extended run

```bash
export TETRAD_BOSS_INPUT_CSV=data/hot_jupiters_20260714_age.csv
export TETRAD_BOSS_VARIABLES=mass,radius,star_teff,orbital_period,star_age
python src/run_tetrad_boss_star_teff_prior.py
```

This run uses [data/hot_jupiters_20260714_age.csv](data/hot_jupiters_20260714_age.csv).

## Super-Earth sanity check

Use [data/20260526_SE_SN.csv](data/20260526_SE_SN.csv) for the Super-Earth sanity check.

## Use your own dataset

1. Prepare a CSV with one row per planet and numeric columns for the variables you want to analyze.
2. Set the input path, variable list, and optional output path.
3. Keep or adjust the host-star prior if your causal assumptions differ.
4. Run the script.

```bash
export TETRAD_BOSS_INPUT_CSV=/absolute/path/to/your_dataset.csv
export TETRAD_BOSS_OUTPUT_DIR=results/my_run
export TETRAD_BOSS_VARIABLES=mass,radius,star_teff,orbital_period
python src/run_tetrad_boss_star_teff_prior.py
```

If you include `F_inc` or `mean_density`, your CSV must also contain the columns needed to compute them.

## Cite this work

Placeholder BibTeX to update once the paper is published:

```bibtex
@article{jin_hot_jupiter_inflation_tbd,
  title   = {Causal Hot Jupiter Inflation},
  author  = {TBD},
  journal = {TBD},
  year    = {TBD},
  note    = {Placeholder citation; update after publication.}
}
```
