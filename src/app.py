"""Menu-bar status indicator for Claude Code.

Polls ``state.json`` (via :mod:`state`) and updates the macOS menu-bar icon
to reflect whether Claude is thinking, idle, stopped, or using a tool.

Usage
-----
Run from the project root:

    uv run status-indicator      # foreground; Ctrl+C to stop
    python src/app.py             # same; runs in background when launched from TTY
"""

import sys

import rumps  # macOS-only GUI framework

from claude_status import ClaudeStatus
from status_config import STATUS_CONFIG, get_status_label
from state import APP_DIR, get_state

# Assets directory (APP_DIR is ~/Projects/tools/status-indicator).
ICONS_DIR = APP_DIR / "assets" / "icons"


# ---------------------------------------------------------------------------
# Menu bar application
# ---------------------------------------------------------------------------


class ClaudeStatusIndicator(rumps.App):
    """A macOS menu-bar icon that tracks Claude Code's runtime state."""

    def __init__(self):
        super().__init__(
            "Claude Status",
            title=get_status_label(ClaudeStatus.NOT_RUNNING),
            template=None,
        )

        self.current_state = None

        self.state_item = rumps.MenuItem(
            get_status_label(ClaudeStatus.NOT_RUNNING)
        )

        self.menu = [
            self.state_item,
            None,
            rumps.MenuItem("Refresh", callback=self.refresh),
        ]

        self.timer = rumps.Timer(self.refresh, 1)
        self.timer.start()

        self.refresh(None)

    def _icon_path(self, state: str) -> str | None:
        """Resolve the icon file for *state*, returning None if missing."""
        config = STATUS_CONFIG.get(state, {})
        icon_name = config.get("icon", "")
        if not icon_name:
            return None
        path = ICONS_DIR / icon_name
        return str(path) if path.is_file() else None

    def refresh(self, _):
        """Sync the menu-bar UI with the current state."""
        state = get_state()

        if state == self.current_state:
            return

        self.current_state = state

        icon_path = self._icon_path(state)

        if icon_path is not None:
            self.icon = icon_path
            self.template = False
            self.title = None
        else:
            # Fallback: no custom icon available.
            self.icon = None
            self.title = f"?"  # generic placeholder

        self.state_item.title = get_status_label(state)

    def quit_app(self, _):
        """Terminate the application."""
        rumps.quit_application()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the status indicator as a foreground process."""

    try:
        ClaudeStatusIndicator().run()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
