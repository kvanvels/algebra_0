#!/usr/bin/env bash
# Run AUCTeX's LaTeX-fill-buffer (LaTeX-aware paragraph fill) over
# chapters/*.tex.
#
#   ./fill_chapters.sh            # dry run: prints a diff, writes nothing
#   ./fill_chapters.sh --apply    # actually rewrites the files
#   ./fill_chapters.sh --apply --files chapters/rings.tex chapters/fields.tex
#
# Uses AUCTeX from your normal package.el installation, so it fills exactly
# as `M-q`/`C-c C-q C-p` would interactively (same fill-column, same AUCTeX
# setup) -- just without loading the rest of your init file.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKER="$SCRIPT_DIR/fill_chapters.el"

apply=0
files=()
while [ $# -gt 0 ]; do
    case "$1" in
        --apply) apply=1 ;;
        --files) shift; while [ $# -gt 0 ]; do files+=("$1"); shift; done ;;
        *) files+=("$1") ;;
    esac
    shift || true
done

if [ ${#files[@]} -eq 0 ]; then
    files=("$SCRIPT_DIR"/chapters/*.tex)
fi

changed=0

for f in "${files[@]}"; do
    tmp="$(mktemp --suffix=.tex)"
    cp "$f" "$tmp"
    emacs --batch -l "$WORKER" "$tmp" >/dev/null 2>&1

    if diff -q "$f" "$tmp" >/dev/null; then
        rm -f "$tmp"
        continue
    fi

    changed=$((changed + 1))
    echo "=== $f ==="
    diff -u "$f" "$tmp" || true

    if [ "$apply" -eq 1 ]; then
        mv "$tmp" "$f"
        echo "  wrote $f"
    else
        rm -f "$tmp"
    fi
    echo
done

if [ "$apply" -eq 1 ]; then
    echo "Done: $changed file(s) refilled."
else
    echo "Dry run: $changed file(s) would change. Re-run with --apply to write changes."
fi
