#!/usr/bin/env bash
# Wrapper for Codex CLI hooks.
# Silently skips if pixi environment is not set up yet.
# Called from hooks.json: bash .codex/hooks/run-hook.sh --hook <event-name>

set -uo pipefail

# Navigate to project root (run-hook.sh is at .codex/hooks/run-hook.sh)
cd "${0%/*}/../.." 2>/dev/null || exit 0

# Skip if pixi is not available
command -v pixi >/dev/null 2>&1 || exit 0

# Skip if pixi environment is not initialized (no pixi.toml)
[[ -f pixi.toml ]] || [[ -f pyproject.toml ]] || exit 0

# Run the hook script via pixi
pixi run python3 .codex/hooks/scripts/hooks.py "$@" 2>/dev/null || exit 0
