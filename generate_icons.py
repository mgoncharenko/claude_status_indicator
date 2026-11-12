
#!/usr/bin/env python3
# Usage (two lines):
#   export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix cairo)/lib:$DYLD_FALLBACK_LIBRARY_PATH"
#   uv run generate_icons.py

from pathlib import Path
import re
import sys

import cairosvg


# Paths relative to this script's location.
ROOT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = ROOT_DIR / "assets" / "source"
OUTPUT_DIR = ROOT_DIR / "assets" / "icons"

SIZE = 40

# Status -> Lucide source filename -> icon color
ICONS = {
    "not-running": ("power", "#8E8E93"),
    "idle": ("coffee", "#8E8E93"),
    "thinking": ("sparkles", "#E8B807"),
    "tool": ("wrench", "#E8B807"),
    "input": ("message-circle-question-mark", "#FF9F0A"),
    "completed": ("circle-check", "#30A46C"),
    "subagent": ("network", "#E8B807"),
    "compacting": ("shrink", "#AF52DE"),
    "plan": ("list-todo", "#AF52DE"),
    "permission": ("shield-question-mark", "#FF9F0A"),
    "error": ("octagon-x", "#FF453A"),
}


def prepare_svg(svg: str, color: str) -> str:
    """Apply the status color to a Lucide SVG."""

    # Replace inherited/currentColor values.
    svg = svg.replace("currentColor", color)

    # Set explicit stroke color on the root SVG.
    svg = re.sub(
        r'(<svg\b[^>]*?)\sstroke="[^"]*"',
        lambda m: m.group(1) + f' stroke="{color}"',
        svg,
        count=1,
    )

    # If the SVG didn't have a stroke attribute, add one.
    if not re.search(r"<svg\b[^>]*\bstroke=", svg):
        svg = re.sub(
            r"<svg\b",
            f'<svg stroke="{color}"',
            svg,
            count=1,
        )

    # Force the expected dimensions.
    svg = re.sub(r'\bwidth="[^"]*"', f'width="{SIZE}"', svg, count=1)
    svg = re.sub(r'\bheight="[^"]*"', f'height="{SIZE}"', svg, count=1)

    # Ensure a transparent background.
    svg = re.sub(
        r"<svg\b",
        '<svg style="background: transparent"',
        svg,
        count=1,
    )

    return svg


def generate_icon(status: str, source_name: str, color: str) -> bool:
    source_file = SOURCE_DIR / f"{source_name}.svg"
    output_file = OUTPUT_DIR / f"{status}.png"

    if not source_file.exists():
        print(f"[MISSING] {source_file.name}")
        return False

    try:
        svg = source_file.read_text(encoding="utf-8")
        svg = prepare_svg(svg, color)

        cairosvg.svg2png(
            bytestring=svg.encode("utf-8"),
            write_to=str(output_file),
            output_width=SIZE,
            output_height=SIZE,
            background_color=None,
        )

        print(f"[OK] {status}.png ({source_name}.svg, {color})")
        return True

    except Exception as exc:
        print(f"[ERROR] {source_file.name}: {exc}")
        return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Source: {SOURCE_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Size:   {SIZE}x{SIZE}")
    print()

    success = 0
    failed = 0

    for status, (source_name, color) in ICONS.items():
        if generate_icon(status, source_name, color):
            success += 1
        else:
            failed += 1

    print()
    print(f"Generated: {success}/{len(ICONS)}")
    print(f"Failed:    {failed}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

