# pixi Package Management

This project uses pixi exclusively for environment and dependency management.

## Required

- Use `pixi install` to install dependencies
- Use `pixi run <task>` to execute project tasks
- Add packages via `pixi add <package>` (conda-forge) or `pixi add --pypi <package>` (PyPI)
- Prefer conda-forge packages over PyPI when available

## Prohibited

- Do NOT use `pip install`, `pip`, or `python -m pip`
- Do NOT use `conda`, `mamba`, or `micromamba` directly
- Do NOT create or activate `venv`, `.venv`, or virtualenvs
- Do NOT modify `requirements.txt` or `setup.py`

## Configuration

- `pixi.toml` or `pyproject.toml` with `[tool.pixi.*]` is the single source of truth
- `.pixi/` directory is git-ignored (local environment cache)
- `pixi.lock` is git-ignored (regenerated from pixi.toml)
