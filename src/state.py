"""Shared state infrastructure for the status indicator.

Provides the persistent state file, hook writers, and state readers that the
menu-bar indicator consumes.  This module has **no GUI dependencies**.
"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------

import fcntl
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths & configuration
# ---------------------------------------------------------------------------

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent  # src/ → project root (contains assets/)

ASSETS_DIR = PROJECT_DIR / "assets"

APP_DIR = Path.home() / "Projects/tools/status-indicator"
STATE_FILE = APP_DIR / "state.json"
LOCK_FILE = APP_DIR / "state.lock"


# ---------------------------------------------------------------------------
# Claude process detection
# ---------------------------------------------------------------------------

CLAUDE_PROCESS = re.compile(
    r"ollama\s+launch\s+claude"
    r"|@anthropic-ai/claude-code"
    r"|(?:^|[\s/])claude(?:[\s]|$)",
    re.IGNORECASE,
)


def is_claude_running() -> bool:
    """Check whether a Claude Code process is running."""
    try:
        result = subprocess.run(
            ["ps", "-axo", "pid=,args="],
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        )

        for line in result.stdout.splitlines():
            parts = line.strip().split(None, 1)

            if len(parts) != 2:
                continue

            pid, command = parts

            if int(pid) == os.getpid():
                continue

            if CLAUDE_PROCESS.search(command):
                return True

    except (subprocess.SubprocessError, OSError, ValueError):
        pass

    return False


# ---------------------------------------------------------------------------
# Current status
# ---------------------------------------------------------------------------

from claude_status import ClaudeStatus  # noqa: E402


def get_state() -> str:
    """Determine the current overall Claude Code status.

    Reads from the shared ``state.json`` file and also checks whether any
    Claude Code process is currently running (falls back to
    :attr:`ClaudeStatus.NOT_RUNNING` or the appropriate session state).
    """
    if not is_claude_running():
        return ClaudeStatus.NOT_RUNNING

    try:
        with open(STATE_FILE) as file:
            data = json.load(file)

        sessions = data.get("sessions", {})
        states = list(sessions.values())

        # Priority when multiple sessions exist.
        if state_values := {s for s in states}:
            if ClaudeStatus.TOOL in state_values:
                return ClaudeStatus.TOOL

            if ClaudeStatus.THINKING in state_values:
                return ClaudeStatus.THINKING

            if ClaudeStatus.IDLE in state_values:
                return ClaudeStatus.IDLE

    except (OSError, json.JSONDecodeError):
        pass

    # No recognized session state — don't assume idle.
    return ClaudeStatus.NOT_RUNNING


# ---------------------------------------------------------------------------
# Hook state management (writers)
# ---------------------------------------------------------------------------

def update_state(event: dict) -> None:
    """Update the state of a Claude Code session based on a hook event."""
    event_name = event.get("hook_event_name", "")
    session_id = event.get("session_id") or "default"

    if event_name == "SessionStart":
        state = ClaudeStatus.IDLE

    elif event_name == "UserPromptSubmit":
        state = ClaudeStatus.THINKING

    elif event_name == "PreToolUse":
        state = ClaudeStatus.TOOL

    elif event_name == "PostToolUse":
        state = ClaudeStatus.THINKING

    elif event_name in ("Stop", "StopFailure"):
        state = ClaudeStatus.IDLE

    elif event_name == "Notification":
        notification = event.get("notification_type", "")

        if notification in ("permission_prompt", "idle_prompt"):
            state = ClaudeStatus.IDLE
        else:
            return

    elif event_name == "SessionEnd":
        state = None

    else:
        return

    APP_DIR.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)

        try:
            data = {}

            if STATE_FILE.exists():
                try:
                    data = json.loads(STATE_FILE.read_text())
                except (json.JSONDecodeError, OSError):
                    pass

            sessions = data.get("sessions", {})

            if state is None:
                sessions.pop(session_id, None)
            else:
                sessions[session_id] = state

            temp_file = STATE_FILE.with_suffix(".tmp")
            temp_file.write_text(
                json.dumps({"sessions": sessions})
            )
            temp_file.replace(STATE_FILE)

        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


# ---------------------------------------------------------------------------
# CLI entry point (for external hook scripts)
# ---------------------------------------------------------------------------

def handle_hook() -> None:
    """Read a hook event from stdin and update the shared state file.

    This is the function invoked by Claude Code's post-tool-use hooks via
    ``python -m main hook`` or equivalently ``python main.py hook`` when
    run as the entry point script.
    """
    try:
        event = json.load(sys.stdin)
        update_state(event)

    except Exception as exc:
        print(
            f"Claude status hook error: {exc}",
            file=sys.stderr,
        )
