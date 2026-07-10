#!/usr/bin/env python3
"""
Reference-cleanup pass, final step: strip the OLD: marker prefix left
by mark_old_references.py once every reference in a chapter has been
manually reviewed/fixed and (for labels) confirmed to still be the
right target.

Run project-wide (no arguments) after finishing a chapter's manual
resolve pass -- it strips every remaining "OLD:<label>" token, in
label definitions and in \\ref/\\Cref/etc. usages alike, across all
chapter files and master.tex. Since definitions and usages are always
renamed in lockstep by mark_old_references.py, this is safe to run
blanket: it never changes which label a reference resolves to, only
removes the marker.

Usage (from the project root):
    python3 scripts/strip_old_prefix.py
"""

import glob
import re


def main():
    files = sorted(set(glob.glob("chapters/*.tex")) | {"master.tex"})
    total = 0
    for f in files:
        text = open(f).read()
        new_text, n = re.subn(r"OLD:([a-zA-Z0-9:._-]+)", r"\1", text)
        if n:
            open(f, "w").write(new_text)
            print(f"{f}: stripped {n}")
            total += n
    print("TOTAL:", total)


if __name__ == "__main__":
    main()
