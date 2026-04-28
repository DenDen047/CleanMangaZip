#!/usr/bin/env python3
"""
Codex CLI Hook Handler
======================
Handles hooks from Codex CLI: SessionStart context injection and sound notifications.

Codex CLI supports 5 hooks (this template uses SessionStart and Stop):
  - SessionStart (v0.114.0+)
  - PreToolUse (v0.117.0+)
  - PostToolUse (v0.117.0+)
  - Stop (v0.114.0+)
  - UserPromptSubmit (v0.116.0+)

Called via: pixi run python3 .codex/hooks/scripts/hooks.py --hook <hook-name>
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HOOK_CONFIG_MAP = {
    "SessionStart": "disableSessionStartHook",
    "Stop": "disableStopHook",
}


def load_config():
    """Load hook configuration with local override fallback."""
    script_dir = Path(__file__).parent
    config_dir = script_dir.parent / "config"

    local_path = config_dir / "hooks-config.local.json"
    default_path = config_dir / "hooks-config.json"

    for path in (local_path, default_path):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
    return {}


def is_hook_disabled(event_name):
    """Check if a hook is disabled in config."""
    config = load_config()
    key = HOOK_CONFIG_MAP.get(event_name, "")
    return config.get(key, False)


def get_session_context():
    """Gather project context for SessionStart injection into model context."""
    lines = []
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        if branch:
            lines.append(f"Git branch: {branch}")
    except Exception:
        pass

    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        lines.append(
            f"Working tree: {'clean' if not status else 'uncommitted changes'}"
        )
    except Exception:
        pass

    lines.append(f"Working directory: {Path.cwd()}")

    readme = Path("CLAUDE.md")
    if readme.exists():
        try:
            content = readme.read_text(encoding="utf-8")[:500]
            lines.append(f"\nProject context (from CLAUDE.md):\n{content}")
        except Exception:
            pass

    return "\n".join(lines)


def play_sound(sound_name):
    """Play a sound file if it exists."""
    script_dir = Path(__file__).parent
    sounds_dir = script_dir.parent / "sounds" / sound_name

    if not sounds_dir.exists():
        return

    for ext in (".wav", ".mp3"):
        sound_file = sounds_dir / f"{sound_name}{ext}"
        if sound_file.exists():
            try:
                subprocess.Popen(
                    ["afplay", str(sound_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except Exception:
                pass
            return


def log_hook_data(event_type):
    """Log hook event to JSONL file."""
    config = load_config()
    if config.get("disableLogging", True):
        return

    script_dir = Path(__file__).parent
    logs_dir = script_dir.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "hook": event_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        log_path = logs_dir / "hooks-log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--hook":
        sys.exit(0)

    event_type = sys.argv[2]

    if is_hook_disabled(event_type):
        sys.exit(0)

    log_hook_data(event_type)

    if event_type == "SessionStart":
        print(get_session_context())

    play_sound(event_type)


if __name__ == "__main__":
    main()
