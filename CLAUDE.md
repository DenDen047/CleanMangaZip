# CleanMangaZip

漫画フォルダ（連番画像が入った1つのフォルダ）に対して、AVIF→WebP変換、不要ファイル削除、一括クロップ、ZIP化を行う CLI ツール。

## Entry point

- `main.py` — 単一ファイル CLI。`pixi run run` または `pixi run python main.py --crop_area auto` で実行。
- `--crop_area auto` は多画像分散コンセンサス方式で全ページ共通の余白を自動検出する (`detect_crop_area()` in `main.py`)。

## Environment

- Package manager: pixi (conda-forge)
- Environment setup: `/pixi-env` skill
- Do NOT use pip, venv, or conda directly

## Build & Test

```bash
pixi install                 # Install dependencies
pixi run test                # Run tests
pixi run lint                # Lint check
pixi run format              # Auto-format
```

## Code Style

- Single-file CLI: `main.py` at repo root. Tests (when added) live in `tests/`.
- Immutable data patterns preferred
- Functions < 50 lines, files < 800 lines

## Orchestration

### Skills (project-level)

| Skill | Purpose |
|-------|---------|
| `/check` | Run all quality checks (test + lint + format) |
| `/plan` | Create a phased plan in `plans/` for cross-model review |

### Agents

| Agent | Purpose |
|-------|---------|
| `project-reviewer` | Review code for project conventions and pixi compliance |

### Hooks

Claude Code hooks (`.claude/hooks/`):

| Event | Script | Behavior |
|-------|--------|----------|
| PostToolUse (Write/Edit) | `post-edit-python.sh` | Auto-format + lint report on .py files |
| PreToolUse (Bash) | `pre-commit-lint.sh` | Block `git commit` if lint errors exist |

Codex CLI hooks (`.codex/hooks/`):

| Event | Behavior |
|-------|----------|
| SessionStart | プロジェクトコンテキスト (git branch, CLAUDE.md) をモデルに注入 |
| Stop | サウンド通知 (Terminal 1 で作業中に Codex の完了を検知) |

> すべての hooks は pixi 環境が未構築でもサイレントスキップする。

### Rules

Project-specific rules are in `.claude/rules/`:
- `pixi.md` -- Package management constraints (pixi-only)

### Cross-model cycle (4 steps)

Claude Code (Terminal 1) と Codex CLI (Terminal 2) のデュアルターミナルで異なるモデルアーキテクチャを交互に使う:

```
Terminal 1 (Claude)          Terminal 2 (Codex)
─────────────────           ─────────────────
1. PLAN                     2. QA REVIEW
   /plan {feature}             計画をレビュー
   → plans/{feature}.md        → Codex Finding を追記
                            
3. IMPLEMENT (新セッション)  4. VERIFY
   phase-by-phase 実装         実装を計画と照合
   各フェーズ後に /check        → 指摘があれば報告
```

- 計画ファイルは `plans/{feature-name}.md` に出力する (ケバブケース)
- PLAN と IMPLEMENT は**別セッション**で行う (コンテキスト汚染を防ぐ)
- 各フェーズに Test Gate を含め、`/check` で検証してから次に進む
- Codex Finding は追記のみ。元のフェーズを書き換えない

### Workflow

```
/pixi-env --> /plan --> codex review --> implement --> /check --> codex verify --> /ai-code-changes --> /git-commits
  環境構築     計画作成   QA レビュー     実装        品質検査    最終検証         セルフレビュー       コミット
            (Terminal 1)  (Terminal 2)  (Terminal 1)           (Terminal 2)
```
