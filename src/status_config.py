"""Configuration for each Claude Code status — labels and icon filenames."""

from claude_status import ClaudeStatus

ICON_DIR_NAME = "icons"  # under assets/ in the project root

STATUS_CONFIG: dict[str, dict[str, str | list]] = {
    ClaudeStatus.NOT_RUNNING: {
        "label": "Claude is not running",
        "icon": "not-running.png",
    },
    ClaudeStatus.IDLE: {
        "label": "Claude is idle",
        "icon": "idle.png",
    },
    ClaudeStatus.THINKING: {
        "label": "Claude is thinking",
        "icon": "thinking.png",
    },
    ClaudeStatus.TOOL: {
        "label": "Claude is using a tool",
        "icon": "tool.png",
    },
    # Reserved for future states:
    ClaudeStatus.PERMISSION: {
        "label": "Permission required",
        "icon": "permission.png",
    },
    ClaudeStatus.INPUT_REQUIRED: {
        "label": "Input required",
        "icon": "input.png",
    },
    ClaudeStatus.COMPLETED: {
        "label": "Session completed",
        "icon": "completed.png",
    },
    ClaudeStatus.ERROR: {
        "label": "An error occurred",
        "icon": "error.png",
    },
    ClaudeStatus.SUBAGENT: {
        "label": "Subagent running",
        "icon": "subagent.png",
    },
    ClaudeStatus.COMPACTING: {
        "label": "Context compaction",
        "icon": "compacting.png",
    },
    ClaudeStatus.PLAN_MODE: {
        "label": "Plan mode",
        "icon": "plan.png",
    },
}


def get_status_label(key: str) -> str:
    """Return the human-readable label for *key*."""
    try:
        return STATUS_CONFIG[key]["label"]
    except KeyError:
        return key
