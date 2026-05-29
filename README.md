# Offshore Microgrid Optimization

This repository contains organized notebooks, supporting Python modules, and archived materials for offshore microgrid optimization experiments and weather data preparation.

## Repository structure

- `notebooks/` – active notebooks in a polished, user-facing layout.
  - `notebooks/00-data-prep/` – data preparation and digital twin notebooks.
  - `notebooks/01-optimization/` – optimization notebooks for GF generation, daily scenario runs, and post-processing.
  - `notebooks/02-weather/` – weather-related notebooks.
    - `notebooks/02-weather/forecast/` – forecast data notebooks.
    - `notebooks/02-weather/collection/` – historical weather collection notebooks.
- `src/` – reusable Python helper scripts and function modules extracted from legacy notebooks.
- `data/backup-artifacts/` – supporting model artifacts, dataset files, and binary resources.
- `archive/legacy-notebooks/` – archived notebook versions and experiment backups.

## Getting started

1. Install Git LFS before cloning/pushing this repository, because several required model/data artifacts are larger than normal GitHub file limits.
2. Create a Python environment from `requirements.txt`. The notebooks were smoke-tested with the local Anaconda Python 3.8 environment.
3. Open the main optimization notebooks in `notebooks/01-optimization/`:
   - `Offshore Microgrid Optimization - IM - GF - Day 1.ipynb`
   - `Offshore Microgrid Optimization - IM - GF - Day 2.ipynb`
   - `Offshore Microgrid Optimization - IM - GF - Day 3.ipynb`
   - `Offshore Microgrid Optimization - IM - GF - Day 4.ipynb`
   - `Offshore Microgrid Optimization - IM - GF - Day 5.ipynb`
   - `Offshore Microgrid Optimization - IM - GF - Day 6.ipynb`
   - `Offshore Microgrid Optimization - IM - GF - Day 7.ipynb`
4. Run notebooks from the repository root or from their own folder. They locate `src/` and `data/backup-artifacts/` automatically.
5. Generated figures, models, and result spreadsheets are written under `outputs/`.

## Validation

Quick repository checks:

```bash
python -m unittest tests/test_repository_readiness.py
```

Notebook setup smoke test:

```bash
python scripts/smoke_test_day_notebooks.py
```

The smoke test executes the setup, data-loading, and model-loading cells for all seven Day notebooks.

Execute the Day notebooks and save cell outputs:

```bash
python scripts/run_day_notebooks.py
```

The runner sets `OFFSHORE_MG_MAX_ITR=1` by default so the notebooks complete in a practical time. For fuller optimization runs, set a larger value before running the script.

## Notes

- `.gitattributes` marks required binary artifacts for Git LFS.
- `outputs/` is ignored so notebook runs do not pollute commits.
- `archive/legacy-notebooks/` keeps earlier versions and historical notebooks separate from the active workflow.
