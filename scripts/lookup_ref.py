#!/usr/bin/env python3
"""
Query old_replacements.json for a cross-chapter reference instead of
re-deriving it from the source PDF. Check this BEFORE searching a
chapter's PDF for a Proposition/Theorem/Example/etc citation -- if a
prior chapter's pass already resolved it, this is instant; if not,
fall back to the PDF as before (and add the result once resolved, see
below).

Usage:
    python3 scripts/lookup_ref.py groups "Proposition 8.11"
    python3 scripts/lookup_ref.py rings "Exercise 4.4"
    python3 scripts/lookup_ref.py groups2                 # dump the whole chapter's table

Exercise-type lookups: prefer regenerating the position index fresh
(scripts/build_position_index.py) over this file -- it's just as fast
and always reflects current source, no staleness risk. This lookup is
most valuable for item-type refs (Proposition/Theorem/Example/etc),
which need PDF content-matching to resolve and are expensive to redo.
"""
import argparse
import json


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("chapter", help="e.g. groups, rings, groups2, irreducibility, prelims")
    ap.add_argument("query", nargs="?", help='e.g. "Proposition 8.11" -- omit to dump the whole chapter')
    args = ap.parse_args()

    data = json.load(open("old_replacements.json"))
    chapter_data = data.get(args.chapter)
    if chapter_data is None:
        print(f"NOT FOUND: chapter {args.chapter!r} has no entry in old_replacements.json at all")
        return

    if args.query is None:
        for k, v in sorted(chapter_data.items()):
            if k.startswith("_"):
                continue
            print(f"{k} -> {v}")
        return

    entry = chapter_data.get(args.query)
    if entry is None:
        print(f"NOT FOUND: {args.query!r} not in {args.chapter}'s table (fall back to PDF search)")
        return
    label = entry.get("label")
    if label is None:
        print(f"KNOWN BUT UNLABELED: {args.query!r} exists in {args.chapter} but has no label yet "
              f"({entry.get('desc', 'no description')})")
        return
    print(label)
    if entry.get("desc"):
        print(f"  ({entry['desc']})")


if __name__ == "__main__":
    main()
