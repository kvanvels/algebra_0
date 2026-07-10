#!/usr/bin/env python3
"""
Reference-cleanup pass, step 1: mark everything in one chapter that
needs review, without changing what the document renders.

For a given chapter file (e.g. chapters/groups.tex) this:

  1. Collects every \\label defined in that chapter (both literal
     \\label{...} and the third-argument style used by our custom
     theorem-like environments, \\begin{env}{title}{label}), and
     renames those labels to OLD:<label> -- in their own definition
     site, AND in every \\ref/\\Cref/\\cref/\\eqref/... that points at
     them anywhere in the project (other chapters may cross-reference
     this chapter's labels). Renaming both sides in lockstep means the
     document still compiles with zero new undefined references; the
     rename is purely a grep-able marker for the manual review pass.

  2. Prepends "OLD" to hardcoded numeric prose references within this
     chapter only, e.g. "Exercise 2.10" -> "OLDExercise 2.10",
     "Chapter~VIII" -> "OLDChapter~VIII". These are invisible to
     LaTeX's undefined-reference check and silently go stale as the
     book is edited, which is the whole reason for this pass.

  3. Prepends "OLD " inside bracket-style used-in pointers within this
     chapter only, e.g. "[4.16]" -> "[OLD 4.16]",
     "[\\S{}IV.2.5]" -> "[OLD \\S{}IV.2.5]".

Usage:
    python3 scripts/mark_old_references.py chapters/groups.tex

Run from the project root (~/wkspc/tex/algebra_0). After this, rebuild
(make check_syntax, twice) and confirm the undefined-reference count
is unchanged before starting the manual resolve pass.
"""

import argparse
import glob
import re
import sys

ENV_NAMES = "defn|prop|lem|thm|coro|exam|exer|fact|rem|axm"
ENV_LABEL_RE = re.compile(
    r"\\begin\{(?:" + ENV_NAMES + r")\}\{[^{}]*\}\{([a-zA-Z0-9:._-]+)\}"
)
LITERAL_LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_MACRO_RE = re.compile(
    r"\\(ref|Cref|cref|eqref|nameref|autoref|pageref|labelcref)\*?(\[[^\]]*\])?\{([^}]*)\}"
)

PROSE_KEYWORDS = (
    "Chapter|Section|Subsection|Theorem|Proposition|Lemma|Corollary|"
    "Definition|Example|Exercise|Remark|Claim|Fact|Notation"
)
PROSE_RE = re.compile(
    r"\b(" + PROSE_KEYWORDS + r")([~ ][IVXLCDM0-9]+(?:\.[0-9]+)?)"
)
BRACKET_RE = re.compile(
    r"\[(\\S\{?\}?[0-9IVXLCDM.]*[^]]*|[0-9]+\.[0-9]+[^]]*)\]"
)


def collect_labels(path):
    text = open(path).read()
    literal = set(LITERAL_LABEL_RE.findall(text))
    env = set(l for l in ENV_LABEL_RE.findall(text) if l)
    return literal | env


def rename_refs_in_text(text, labels):
    def repl(m):
        cmd, opt, arg = m.group(1), m.group(2) or "", m.group(3)
        keys = arg.split(",")
        new_keys = ["OLD:" + k if k in labels else k for k in keys]
        return f"\\{cmd}{opt}{{{','.join(new_keys)}}}"

    return REF_MACRO_RE.sub(repl, text)


def rename_label_defs_in_text(text, labels):
    def literal_repl(m):
        k = m.group(1)
        return f"\\label{{OLD:{k}}}" if k in labels else m.group(0)

    text = LITERAL_LABEL_RE.sub(literal_repl, text)

    def env_repl(m):
        full, k = m.group(0), m.group(1)
        if k not in labels:
            return full
        idx = full.rindex(k)
        return full[:idx] + "OLD:" + k + full[idx + len(k):]

    return ENV_LABEL_RE.sub(env_repl, text)


def mark_prose_and_brackets(text):
    """Prepend OLD markers to hardcoded prose refs and bracket
    used-in pointers, skipping the commented-out portion of each
    line (text after an unescaped %)."""
    prose_n = 0
    bracket_n = 0
    out_lines = []
    for line in text.split("\n"):
        if line.lstrip().startswith("%"):
            out_lines.append(line)
            continue
        m = re.search(r"(?<!\\)%", line)
        head, tail = (line[: m.start()], line[m.start():]) if m else (line, "")

        def prose_repl(mo):
            nonlocal prose_n
            prose_n += 1
            return "OLD" + mo.group(1) + mo.group(2)

        head = PROSE_RE.sub(prose_repl, head)

        def bracket_repl(mo):
            nonlocal bracket_n
            bracket_n += 1
            return "[OLD " + mo.group(1) + "]"

        head = BRACKET_RE.sub(bracket_repl, head)
        out_lines.append(head + tail)
    return "\n".join(out_lines), prose_n, bracket_n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("chapter", help="path to the chapter file, e.g. chapters/groups.tex")
    args = ap.parse_args()

    target = args.chapter
    labels = collect_labels(target)
    print(f"Collected {len(labels)} labels from {target}")

    all_files = sorted(set(glob.glob("chapters/*.tex")) | {"master.tex"})
    changed = {}
    for f in all_files:
        text = open(f).read()
        orig = text
        text = rename_refs_in_text(text, labels)
        if f == target:
            text = rename_label_defs_in_text(text, labels)
        if text != orig:
            changed[f] = text

    for f, text in changed.items():
        open(f, "w").write(text)
        marker = " (label rename)" if f != target else " (label rename + defs)"
        print(f"  updated {f}{marker}")

    # Prose + bracket marking only within the target chapter.
    text = open(target).read()
    text, prose_n, bracket_n = mark_prose_and_brackets(text)
    open(target, "w").write(text)
    print(f"Marked {prose_n} hardcoded prose refs and {bracket_n} bracket pointers in {target}")


if __name__ == "__main__":
    main()
