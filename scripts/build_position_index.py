#!/usr/bin/env python3
"""
Build a "section.position -> label" lookup table for a chapter, based
on Aluffi's original numbering convention: theorem-like environments
(defn/prop/lem/thm/coro/exam/fact/rmk/claim) share ONE counter per
section; \\begin{exer}...\\end{exer} environments have a SEPARATE
counter, also reset per section.

This is a hypothesis generator, not ground truth: content in the
chapter may have been added/reordered/removed since the original
numbering was fixed, so always sanity-check the target's content
against the original PDF before trusting a position match, especially
for anything that looks surprising.

Usage:
    python3 scripts/build_position_index.py chapters/groups.tex
"""
import argparse
import re

ITEM_ENVS = "defn|prop|lem|thm|coro|exam|fact|rem|axm"
BEGIN_RE = re.compile(
    r"^\\begin\{(" + ITEM_ENVS + r"|exer)\}\{[^{}]*\}\{([a-zA-Z0-9:._-]*)\}"
)
# Only used as a section-BOUNDARY marker -- titles may span multiple lines
# or contain nested braces (\texorpdfstring{...}{...}), so we don't try to
# capture the full title, just detect that a new \section starts here.
SECTION_START_RE = re.compile(r"^\\section\{")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("chapter")
    args = ap.parse_args()

    sec = 0
    item_n = 0
    exer_n = 0
    item_table = {}
    exer_table = {}
    section_starts = []

    for lineno, line in enumerate(open(args.chapter), 1):
        if SECTION_START_RE.match(line):
            sec += 1
            item_n = 0
            exer_n = 0
            section_starts.append(lineno)
            continue
        m = BEGIN_RE.match(line)
        if m:
            env, label = m.group(1), m.group(2)
            if env == "exer":
                exer_n += 1
                key = f"{sec}.{exer_n}"
                exer_table[key] = (label, lineno)
            else:
                item_n += 1
                key = f"{sec}.{item_n}"
                item_table[key] = (env, label, lineno)

    print(f"=== Sections in {args.chapter} ===")
    print(f"(non-exercise items share one counter per section; exercises have their own)")
    for i, lineno in enumerate(section_starts, 1):
        print(f"  section {i} starts at line {lineno}")
    print()
    print("=== Item table (Definition/Proposition/Lemma/Theorem/Corollary/Example/...) ===")
    for k in sorted(item_table, key=lambda k: tuple(map(int, k.split(".")))):
        env, label, lineno = item_table[k]
        print(f"  {k:>8}  {env:5} {label or '(unlabeled)':50} line {lineno}")
    print()
    print("=== Exercise table ===")
    for k in sorted(exer_table, key=lambda k: tuple(map(int, k.split(".")))):
        label, lineno = exer_table[k]
        print(f"  {k:>8}  exer  {label or '(unlabeled)':50} line {lineno}")


if __name__ == "__main__":
    main()
