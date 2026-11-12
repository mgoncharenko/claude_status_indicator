"""Enumerated statuses for Claude Code's runtime state."""

import enum


class ClaudeStatus(enum.StrEnum):
    """All possible states a Claude Code session can be in."""

    NOT_RUNNING = "not_running"
    IDLE = "idle"
    THINKING = "thinking"
    TOOL = "tool"

    # Reserved for future states:
    PERMISSION = "permission"
    INPUT_REQUIRED = "input_required"
    COMPLETED = "completed"
    ERROR = "error"
    SUBAGENT = "subagent"
    COMPACTING = "compacting"
    PLAN_MODE = "plan_mode"


__all__ = ["ClaudeStatus"]
