#!/usr/bin/env python3
"""Rename LaTeX labels across all chapter files.

Usage:
    python scripts/rename_labels.py mapping.json           # dry run (default)
    python scripts/rename_labels.py mapping.json --apply    # actually write changes

mapping.json is a JSON object: {"old:label": "new:label", ...}

Matching is word-bounded: a label is only replaced when it is not preceded or
followed by a "label character" (word char, dot, colon, hyphen). This keeps
"exer:groups2:1.1" from matching inside "exer:groups2:1.13".
"""
import argparse
import json
import re
import sys
from pathlib import Path

LABEL_CHAR = r'[\w.:\-]'
CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "chapters"


def build_pattern(label: str) -> re.Pattern:
    return re.compile(
        rf'(?<!{LABEL_CHAR}){re.escape(label)}(?!{LABEL_CHAR})'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapping", help="JSON file mapping old labels to new labels")
    parser.add_argument("--apply", action="store_true", help="write changes (default is dry run)")
    parser.add_argument("--files", nargs="*", help="restrict to specific files (default: all chapters/*.tex)")
    args = parser.parse_args()

    mapping = json.loads(Path(args.mapping).read_text())
    if not mapping:
        print("mapping is empty; nothing to do")
        return

    # sanity check for collisions: no new label should collide with another
    # mapping's old label unintentionally, and no duplicate new labels.
    new_labels = list(mapping.values())
    if len(new_labels) != len(set(new_labels)):
        seen = {}
        for old, new in mapping.items():
            seen.setdefault(new, []).append(old)
        dupes = {k: v for k, v in seen.items() if len(v) > 1}
        print(f"ERROR: duplicate new labels: {dupes}", file=sys.stderr)
        sys.exit(1)

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = sorted(p for p in CHAPTERS_DIR.glob("*.tex") if p.is_file())

    patterns = {old: build_pattern(old) for old in mapping}

    total_changes = 0
    for path in files:
        text = path.read_text()
        lines = text.splitlines(keepends=True)
        file_changes = []
        new_lines = []
        for lineno, line in enumerate(lines, start=1):
            new_line = line
            for old, new in mapping.items():
                if patterns[old].search(new_line):
                    new_line = patterns[old].sub(new, new_line)
            if new_line != line:
                file_changes.append((lineno, line.rstrip("\n"), new_line.rstrip("\n")))
            new_lines.append(new_line)

        if file_changes:
            total_changes += len(file_changes)
            print(f"\n=== {path} ({len(file_changes)} line(s)) ===")
            for lineno, old_line, new_line in file_changes:
                print(f"  L{lineno}:")
                print(f"    - {old_line.strip()}")
                print(f"    + {new_line.strip()}")
            if args.apply:
                path.write_text("".join(new_lines))

    print(f"\n{'Applied' if args.apply else 'Would change'} {total_changes} line(s) total"
          f" across {len(files)} file(s) searched.")
    if not args.apply and total_changes:
        print("Dry run only — rerun with --apply to write changes.")


if __name__ == "__main__":
    main()
