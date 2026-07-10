#!/usr/bin/env python3
"""
Reference-cleanup pass: verify every \\ref/\\Cref/\\cref/\\eqref citation
in a chapter that targets a label DEFINED in that same chapter is
spelled exactly right -- catches the single most common mistake made
while resolving prose refs and bracket pointers by hand: writing
\\Cref{some:label} when the label is still (mid-cleanup) defined as
\\label{OLD:some:label}, or vice versa after stripping.

This is more reliable than grepping master_fastcheck.log for
"undefined" warnings, for two reasons:
  1. That log can be non-UTF-8 (pdflatex, accented characters) and
     silently break plain grep -- see feedback_pdflatex_log_grep_binary
     in memory.
  2. Long warning lines wrap in the log and truncate mid-label, so a
     grep -c can under-count real mismatches.

This script instead directly compares the set of labels DEFINED in the
chapter (both literal \\label{...} and the third-argument style used by
our custom theorem-like environments) against the set of labels CITED
from within the same file, and flags any citation that doesn't match a
definition but would if OLD: were added or removed. Citations to
labels genuinely owned by OTHER chapters are not flagged (expected,
since this only knows about the one file).

Usage:
    python3 scripts/verify_own_labels.py chapters/irreducibility.tex
"""
import argparse
import re

LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
ENV_LABEL_RE = re.compile(
    r"\\begin\{(?:defn|prop|lem|thm|coro|exam|exer|fact|rem|axm)\}\{[^{}]*\}\{([a-zA-Z0-9:._-]+)\}"
)
REF_RE = re.compile(r"\\(?:ref|Cref|cref|eqref)\{([^}]*)\}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("chapter")
    args = ap.parse_args()

    text = open(args.chapter).read()
    defined = set(LABEL_RE.findall(text))
    defined |= set(l for l in ENV_LABEL_RE.findall(text) if l)

    cited = set()
    for m in REF_RE.finditer(text):
        for k in m.group(1).split(","):
            cited.add(k.strip())

    mismatches = []
    for c in cited:
        if c in defined:
            continue
        if c.startswith("OLD:") and c[4:] in defined:
            mismatches.append((c, c[4:]))
        elif ("OLD:" + c) in defined:
            mismatches.append((c, "OLD:" + c))

    if not mismatches:
        print(f"OK: no OLD: prefix mismatches in {args.chapter}")
        return

    print(f"{len(mismatches)} OLD: prefix mismatches found:")
    for cited_as, should_be in sorted(set(mismatches)):
        print(f"  cited as {cited_as!r}, should be {should_be!r}")


if __name__ == "__main__":
    main()
