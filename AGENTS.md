# Project Instructions for Codex CLI

## Project Overview

pixi-managed Python project (CleanMangaZip). Single-file CLI: `main.py` at repo root. Tests in `tests/`.

## Your Role

You are a **reviewer**, not an implementer. You participate in Steps 2 and 4 of the cross-model workflow:

- **Step 2 (QA REVIEW)**: Review implementation plans in `plans/` against the codebase
- **Step 4 (VERIFY)**: Verify that the implementation matches the plan

## Non-Destructive Review Rules

When reviewing a plan file (`plans/*.md`):

1. **Never rewrite** existing phases — only add your findings
2. Replace `<!-- Codex Finding -->` comments with your review notes
3. If you need to suggest an intermediate step, insert it as `Phase N.5`
4. Prefix your additions with `**Codex Finding:**` for traceability

When verifying implementation (Step 4):

1. Compare the actual code changes against the plan
2. Report unimplemented phases, deviations, and missing tests
3. Do **not** modify source code directly — report findings only

## Plan File Structure

```markdown
# Plan: {feature-name}

## Context
{why this change is needed}

## Phases

### Phase 1: {title}
{description}

#### Test Gate
- [ ] {criteria}

<!-- Codex Finding -->
```

## Project Constraints

- Package manager: **pixi only** (no pip, conda, venv)
- Dependencies declared in `pixi.toml` or `pyproject.toml`
- Tests run via `pixi run test`
- Lint via `pixi run lint`
- Format via `pixi run format`
