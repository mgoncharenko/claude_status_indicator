#!/usr/bin/env python3
"""Claude Code hook entry point — processes stdin events.

Reads a JSON event from stdin and writes the resulting state to state.json.
No GUI — just accept the hook and exit.
"""

from state import handle_hook


def main() -> None:
    """Process the incoming hook event and update shared state."""
    handle_hook()


if __name__ == "__main__":
    main()
