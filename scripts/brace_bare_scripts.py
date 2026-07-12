#!/usr/bin/env python3
"""Add braces around bare sub/superscript blackboard-bold macros.

Fixes patterns like `_\\R` or `^\\N` (a single-letter macro directly after
_ or ^, with no braces) to `_{\\R}` / `^{\\N}`. Under this document's
unicode-math setup, an unbraced macro script causes a "Missing { inserted"
cascade, even though it's legal in plain TeX. Every other occurrence in the
book already braces these, so this brings stragglers in line.

Usage:
    python scripts/brace_bare_scripts.py            # dry run (default)
    python scripts/brace_bare_scripts.py --apply     # write changes
"""
import argparse
import re
from pathlib import Path

MACROS = "RCQZNAF"
PATTERN = re.compile(rf'([_^])\\([{MACROS}])(?![a-zA-Z{{}}])')
CHAPTERS_DIR = Path(__file__).resolve().parent.parent / "chapters"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes (default is dry run)")
    args = parser.parse_args()

    files = sorted(p for p in CHAPTERS_DIR.glob("*.tex") if p.is_file())

    total_changes = 0
    for path in files:
        text = path.read_text()
        lines = text.splitlines(keepends=True)
        file_changes = []
        new_lines = []
        for lineno, line in enumerate(lines, start=1):
            new_line = PATTERN.sub(r'\1{\\\2}', line)
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
