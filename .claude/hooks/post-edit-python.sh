#!/usr/bin/env bash
# Auto-format and lint Python files after Write/Edit tool calls.
# Receives tool event JSON via stdin.
# - Format: auto-applied (ruff format)
# - Lint: issues reported via stdout (informational, does not block)
#
# Requires: ruff available in the pixi environment.
# Silently skips if pixi env is not set up yet.

set -uo pipefail

# Parse file_path from stdin JSON
file_path=$(pixi run python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    ti = data.get('tool_input', {})
    if isinstance(ti, str):
        ti = json.loads(ti)
    print(ti.get('file_path', ''))
except Exception:
    pass
" 2>/dev/null) || exit 0

# Only process Python files
[[ -n "$file_path" ]] || exit 0
[[ "$file_path" == *.py ]] || exit 0
[[ -f "$file_path" ]] || exit 0

cd "${CLAUDE_PROJECT_DIR:-.}"

# Auto-format (silent, modifies file in place)
pixi run ruff format "$file_path" 2>/dev/null || true

# Lint check (stdout reports issues for Claude to see)
pixi run ruff check "$file_path" 2>/dev/null || true
