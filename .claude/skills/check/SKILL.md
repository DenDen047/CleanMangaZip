---
name: check
description: Run all quality checks (test, lint, format verification)
user-invocable: true
allowed-tools:
  - Bash
  - Read
---

Run all quality checks for this project. Execute each step and report results.

## Steps

1. Verify `pixi.toml` or `pyproject.toml` exists. If not, stop and tell the user to run `/pixi-env` first.
2. Run tests: `pixi run test`
3. Run linter: `pixi run lint`
4. Check formatting: `pixi run format --check` (if supported) or `pixi run format`

## Output

After all checks complete, provide a summary:

| Check  | Status |
|--------|--------|
| test   | pass/fail |
| lint   | pass/fail |
| format | pass/fail |

If any check fails, show the specific errors with file locations.
