#!/usr/bin/env python3
"""
Read all .aux files and produce a sorted list of labels,
flagging duplicates and showing source file and page.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

def extract_top_arg(s, pos):
    """Extract the content of a single {}-delimited argument starting at pos.
    Returns (content, end_pos) or (None, pos) if no { at pos."""
    if pos >= len(s) or s[pos] != '{':
        return None, pos
    depth = 0
    start = pos + 1
    for i in range(pos, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return s[start:i], i + 1
    return None, pos

def parse_newlabel(line):
    """Parse \\newlabel{key}{{counter}{page}{title}{anchor}{extra}}.
    Returns (key, page) or None."""
    m = re.match(r'\\newlabel\{', line)
    if not m:
        return None
    pos = m.end() - 1          # points at the opening {
    key, pos = extract_top_arg(line, pos)
    if key is None:
        return None
    outer, pos = extract_top_arg(line, pos)
    if outer is None:
        return None
    # outer is like {counter}{page}{title}...
    # extract the first two sub-args
    _, p2 = extract_top_arg(outer, 0)
    page, _ = extract_top_arg(outer, p2)
    return key, page or '?'

def main():
    project = Path(__file__).parent
    aux_files = sorted(project.glob('*.aux'))

    if not aux_files:
        print('No .aux files found. Run make first.')
        sys.exit(1)

    # labels[key] = list of (page, source_aux)
    labels = defaultdict(list)

    for aux in aux_files:
        try:
            text = aux.read_text(errors='replace')
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith(r'\newlabel{'):
                continue
            result = parse_newlabel(line)
            if result is None:
                continue
            key, page = result
            if key.endswith('@cref') or key == '':
                continue
            labels[key].append((page, aux.name))

    if not labels:
        print('No labels found.')
        sys.exit(0)

    duplicates = {k: v for k, v in labels.items() if len(v) > 1}
    unique     = {k: v for k, v in labels.items() if len(v) == 1}

    if duplicates:
        print(f'{"="*60}')
        print(f'DUPLICATE LABELS ({len(duplicates)})')
        print(f'{"="*60}')
        for key in sorted(duplicates):
            print(f'  {key}')
            for page, src in duplicates[key]:
                print(f'      page {page:>4}  [{src}]')
        print()

    print(f'{"="*60}')
    print(f'ALL LABELS ({len(labels)} total, {len(duplicates)} duplicates)')
    print(f'{"="*60}')
    for key in sorted(unique):
        page, src = unique[key][0]
        print(f'  {key:<50}  p.{page:<5}  [{src}]')

if __name__ == '__main__':
    main()
