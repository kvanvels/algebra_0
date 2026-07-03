#!/usr/bin/env python3
r"""
Regex find-and-replace over chapters/*.tex.

Edit the RULES list below, then run:

    ./regex_replace.py            # dry run: prints a diff-like preview, writes nothing
    ./regex_replace.py --apply    # actually rewrites the files
    ./regex_replace.py --apply --files chapters/rings.tex chapters/fields.tex

Each rule is (pattern, replacement, flags). `pattern` and `replacement`
follow Python `re` syntax (see https://docs.python.org/3/library/re.html):
  - replacement can use backreferences: r'\1', r'\g<name>'
  - flags is usually 0, or re.MULTILINE / re.DOTALL / re.IGNORECASE (bitwise-or
    them with `|` if you need more than one)

Example rules:

    RULES = [
        # a'  ->  a'   (fix OCR '\setminus' standing in for a prime)
        (r"([A-Za-z])\\setminus(?!\\setminus)", r"\1'", 0),

        # \Cref at the *start* of a sentence should be capitalized; this
        # rule only touches the lowercase form after ". " or at line start
        (r"(^|\. )\\cref\{", r"\1\\Cref{", re.MULTILINE),

        # collapse doubled blank lines
        (r"\n{3,}", "\n\n", 0),
    ]
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# EDIT THIS: each tuple is (pattern, replacement, flags)
# ---------------------------------------------------------------------------
RULES = [
    (r"\\operatorname\{(Hom|Obj|End|Aut|id)\}", r"\\\1", 0),
    (r"\\operatorname\{im\}", r"\\image", 0),
]
# ---------------------------------------------------------------------------


def iter_matches(text, pattern, flags):
    return list(re.finditer(pattern, text, flags))


def preview(path, text, pattern, replacement, flags):
    matches = iter_matches(text, pattern, flags)
    if not matches:
        return 0
    print(f"\n{path}  ({len(matches)} match{'es' if len(matches) != 1 else ''} for /{pattern}/)")
    for m in matches[:10]:
        line_no = text.count("\n", 0, m.start()) + 1
        old = m.group(0)
        new = re.sub(pattern, replacement, old, count=1, flags=flags)
        old_disp = old if len(old) <= 60 else old[:57] + "..."
        new_disp = new if len(new) <= 60 else new[:57] + "..."
        print(f"    line {line_no:>5}:  {old_disp!r}  ->  {new_disp!r}")
    if len(matches) > 10:
        print(f"    ... and {len(matches) - 10} more")
    return len(matches)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write changes to disk (default: dry run only)")
    ap.add_argument("--files", nargs="*", help="restrict to these files (default: all chapters/*.tex)")
    args = ap.parse_args()

    if not RULES:
        print("RULES is empty -- edit regex_replace.py and add (pattern, replacement, flags) tuples.")
        sys.exit(1)

    project = Path(__file__).parent
    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = sorted((project / "chapters").glob("*.tex"))

    total_matches = 0
    total_files_changed = 0

    for path in paths:
        text = path.read_text(encoding="utf-8")
        new_text = text
        file_matches = 0

        for pattern, replacement, flags in RULES:
            if not args.apply:
                file_matches += preview(path, new_text, pattern, replacement, flags)
            new_text, n = re.subn(pattern, replacement, new_text, flags=flags)
            file_matches += n if args.apply else 0

        total_matches += file_matches

        if args.apply and new_text != text:
            path.write_text(new_text, encoding="utf-8")
            total_files_changed += 1
            print(f"  wrote {path}  ({file_matches} replacement{'s' if file_matches != 1 else ''})")

    print()
    if args.apply:
        print(f"Done: {total_matches} replacements across {total_files_changed} file(s).")
    else:
        print(f"Dry run: {total_matches} match(es) found. Re-run with --apply to write changes.")


if __name__ == "__main__":
    main()
