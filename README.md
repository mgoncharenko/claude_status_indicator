# status-indicator

A macOS menu-bar icon that reflects [Claude Code](https://claude.ai/code)'s runtime state — thinking, idle, using a tool, etc.

## Setup

1. Install [uv](https://github.com/astral-sh/uv):

   ```bash
   brew install uv
   ```

2. Install the project's dependencies:

   ```bash
   uv sync
   ```

## Iconography

The app ships with 11 pre-bundled 40×40 PNG icons in `assets/icons/`, rendered from Lucide SVGs. The following table maps each Claude Code status to its icon, color, and original Lucide name:

| State            | Icon filename   | Lucide name         | Color   |
| ---------------- | --------------- | ------------------- | ------- |
| Not running      | `not-running.png` | power             | #8E8E93 |
| Idle             | `idle.png`        | coffee            | #8E8E93 |
| Thinking         | `thinking.png`    | sparkles          | #E8B807 |
| Using a tool     | `tool.png`        | wrench            | #E8B807 |
| Input required   | `input.png`       | message-circle-question-mark | #FF9F0A |
| Completed        | `completed.png`   | circle-check      | #30A46C |
| Subagent running | `subagent.png`    | network           | #E8B807 |
| Compacting       | `compacting.png`  | shrink            | #AF52DE |
| Plan mode        | `plan.png`        | list-todo         | #AF52DE |
| Permission required | `permission.png` | shield-question-mark | #FF9F0A |
| Error            | `error.png`       | octagon-x         | #FF453A |

To replace these with your own SVGs, see the final section of this README.

## Claude Code Hooks

Merge [`claude_settings.json`](claude_settings.json) into your `~/.claude/settings.json` to wire the hooks that invoke `src/hook.py`.

### How it works

The app follows a two-component model:

1. **`src/hook.py`** runs as a Claude Code post-tool hook. It reads a JSON event from stdin and writes the resulting state to `state.json`.
2. **`src/app.py`** is a standalone macOS menu-bar GUI that polls `state.json` every second and updates the icon/title to match Claude's current state.

This separation keeps both components self-contained — `hook.py` accepts no arguments and expects JSON on stdin; the GUI reads from a file.

### Event → State mapping

| Hook event        | Written state     | When it fires                    |
| ----------------- | ----------------- | -------------------------------- |
| `SessionStart`    | `idle`            | New session opens                |
| `UserPromptSubmit`| `thinking`        | You submit a prompt              |
| `PreToolUse`      | `tool`            | Claude begins executing a tool   |
| `PostToolUse`     | `thinking`        | Tool execution completes         |
| `Stop` / `StopFailure` | `idle`       | Session is stopped               |
| `SessionEnd`      | _(removed)_       | Session closes entirely          |
| `Notification`    | `idle`            | Matches `permission_prompt\|idle_prompt` |

> **Tip:** After adding the hooks, keep `src/app.py` running and open Claude Code — the menu-bar icon should update as sessions start, tools run, etc.

## Running

```bash
python src/app.py    # foreground process; Ctrl+C to stop
uv run status        # same; blocks until interrupted
```

Run from the project root. A menu-bar icon appears and polls `state.json` every second, updating the icon/title to match Claude's state. A "Quit" item sits in the app's dropdown (or use Cmd+Q from the Dock).

## Generate Custom Icons

The default icons are bundled in `assets/icons/`. To replace them with custom ones:

1. Install [Cairo](https://www.cairographics.org/) (only needed for icon generation, not for running the app):

   ```bash
   brew install cairo
   ```

2. Place your SVGs into `assets/source/`, one per icon. Filenames must match the Lucide names used in [`generate_icons.py`](generate_icons.py):

   ```
   lucide/icons/power.svg           → "power"
   lucide/icons/sparkles.svg        → "sparkles"
   ```

   To grab Lucide's full set:

   ```bash
   git clone --depth=1 --filter=blob:none \
     https://github.com/lucide-icons/lucide.git lucide-source
   cp -n lucide-source/icons/*.svg assets/source/
   rm -rf lucide-source
   ```

3. Edit the `ICONS` dictionary in [`generate_icons.py`](generate_icons.py) to pick source names and colors.

4. Run the generation script:

   ```bash
   export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix cairo)/lib:$DYLD_FALLBACK_LIBRARY_PATH"
   uv run generate_icons.py
   ```

   > **Why the env var?**  macOS ships its own outdated `libpng`; this ensures Cairo uses the Homebrew version.

   The script reads each `*.svg` from `assets/source/`, applies the configured color, and writes updated 40×40 PNGs to `assets/icons/`.
