#!/usr/bin/env bash
# Run lint and type check before git commit.
# Blocks the commit (exit 2) if critical issues are found.
# Receives tool event JSON via stdin.
#
# Triggered on PreToolUse for Bash tool calls matching "git commit".

set -uo pipefail

# Parse command from stdin JSON
command=$(pixi run python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    ti = data.get('tool_input', {})
    if isinstance(ti, str):
        ti = json.loads(ti)
    print(ti.get('command', ''))
except Exception:
    pass
" 2>/dev/null) || exit 0

# Only intercept git commit commands
[[ "$command" == git\ commit* ]] || exit 0

cd "${CLAUDE_PROJECT_DIR:-.}"

# Run lint (exit 2 = block the tool call if lint fails)
if ! pixi run ruff check . 2>/dev/null; then
    echo "Lint errors found. Fix them before committing."
    exit 2
fi
