# Causal Hot Jupiter Inflation

<p align="center"><strong>☀️ ~~~ 🪐 ➜ 🔗</strong></p>

Code, data, and manuscript assets for the study of hot Jupiter inflation with causal discovery.

## Repository layout

```text
Causal-Hot-Jupiter-Inflation/
├── data/
│   ├── 20260526_SE_SN.csv
│   ├── hot_jupiters_20260403.csv
│   └── hot_jupiters_20260714_age.csv
├── docs/
│   └── Exoplanets_v2.pdf
├── results/
├── src/
│   └── run_tetrad_boss_star_teff_prior.py
├── LICENSE
└── README.md
```

## Included files

- `docs/Exoplanets_v2.pdf` - paper manuscript.
- `data/hot_jupiters_20260403.csv` - baseline hot-Jupiter table used by default in the script.
- `data/hot_jupiters_20260714_age.csv` - variant that includes `star_age`.
- `data/20260526_SE_SN.csv` - larger exoplanet table with measurement uncertainties.
- `src/run_tetrad_boss_star_teff_prior.py` - causal discovery workflow based on Tetrad BOSS.

## What the script does

The main script:

1. loads a CSV dataset,
2. selects the requested variables,
3. standardizes complete cases,
4. applies causal prior constraints,
5. runs Tetrad BOSS,
6. writes graph and summary files into `results/`.

The current default variable set is:

- `mass`
- `radius`
- `star_teff`
- `orbital_period`

Optional derived variables supported by the script:

- `mean_density`
- `F_inc`

## Python and system dependencies

The uploaded code imports these Python libraries:

- `pandas`
- `pydot`
- `pytetrad`

Install them with:

```bash
python -m pip install pandas pydot pytetrad
```

You also need:

- **Java**: required by Tetrad. Set `JAVA_HOME` to your local JDK installation.
- **Graphviz**: required so `pydot` can render `.png` and `.pdf` graph outputs.

Example setup:

```bash
export JAVA_HOME=/path/to/your/jdk
python -m pip install pandas pydot pytetrad
```

If Graphviz is not already installed on your machine, install it with your system package manager before running the script.

## Reproducing the uploaded workflow

From the repository root:

```bash
python src/run_tetrad_boss_star_teff_prior.py
```

By default this uses:

- input dataset: `data/hot_jupiters_20260403.csv`
- output directory: `results/tetrad_boss_star_teff_not_child`
- score: `sem_bic`

Expected outputs include:

- `selected_complete_cases.csv`
- `selected_complete_cases_standardized.csv`
- `knowledge.txt`
- `graph.txt`
- `graph.dot`
- `graph.png`
- `graph.pdf`
- `adjacency_matrix.csv`
- `edges.csv`
- `forbidden_edges.csv`
- `tetrad_boss_results_summary.json`

## Runtime options

The script is controlled with environment variables.

| Variable | Purpose | Default |
| --- | --- | --- |
| `TETRAD_BOSS_INPUT_CSV` | Input dataset path | `data/hot_jupiters_20260403.csv` |
| `TETRAD_BOSS_OUTPUT_DIR` | Output directory | `results/tetrad_boss_star_teff_not_child` |
| `TETRAD_BOSS_VARIABLES` | Comma-separated variable list | `mass,radius,star_teff,orbital_period` |
| `TETRAD_BOSS_SCORE` | Tetrad score choice | `sem_bic` |
| `TETRAD_BOSS_ALLOWED_TARGET_PARENTS` | Allowed parents of `star_teff` | `star_age` |
| `TETRAD_BOSS_ROOT_CAUSES` | Variables forbidden from being children | `star_age` |

Supported scores in the uploaded code:

- `sem_bic`
- `basis_function_bic`
- `basis_function_bic_fs`
- `trff_bic`
- `ffml`

## Example: run with the age dataset

```bash
export JAVA_HOME=/path/to/your/jdk
export TETRAD_BOSS_INPUT_CSV=data/hot_jupiters_20260714_age.csv
export TETRAD_BOSS_VARIABLES=mass,radius,star_teff,orbital_period,star_age
export TETRAD_BOSS_ALLOWED_TARGET_PARENTS=star_age
export TETRAD_BOSS_ROOT_CAUSES=star_age

python src/run_tetrad_boss_star_teff_prior.py
```

## Trying the method on your own dataset

To reuse the workflow with a new CSV file:

1. prepare a CSV table with one row per object and a first column that can serve as an index,
2. include the variables you want to analyze as numeric columns,
3. point `TETRAD_BOSS_INPUT_CSV` to that file,
4. set `TETRAD_BOSS_VARIABLES` to the columns you want to pass into Tetrad,
5. if you use `F_inc`, also include `star_mass`, `star_teff`, and `orbital_period`,
6. if you use `mean_density`, also include `mass` and `radius`,
7. update the prior variables if your dataset uses a different causal assumption.

Example:

```bash
export JAVA_HOME=/path/to/your/jdk
export TETRAD_BOSS_INPUT_CSV=/absolute/path/to/your_dataset.csv
export TETRAD_BOSS_OUTPUT_DIR=results/my_dataset_run
export TETRAD_BOSS_VARIABLES=mass,radius,star_teff,orbital_period
export TETRAD_BOSS_ALLOWED_TARGET_PARENTS=
export TETRAD_BOSS_ROOT_CAUSES=

python src/run_tetrad_boss_star_teff_prior.py
```

The script automatically drops rows with missing values among the selected variables, standardizes the retained rows, and writes a machine-readable summary of the run.

## Notes

- Paths can be given as absolute paths or as paths relative to the repository root.
- Results are not committed by default; they are generated when you run the analysis locally.
- The manuscript PDF and uploaded datasets are preserved in `docs/` and `data/` for reference and reuse.
