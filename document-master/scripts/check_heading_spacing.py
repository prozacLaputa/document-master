#!/usr/bin/env python3
"""Read-only heading-gap audit for rich-text XML or a Lark fetch JSON response.

Not a Markdown parser or a visual acceptance test. No network or write operations.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def load_blocks(raw):
    raw = raw.strip()
    if raw.startswith('{'):
        data = json.loads(raw)
        raw = data['data']['document']['content'].strip()
    if not raw.startswith('<'):
        raise ValueError('Expected rich-text XML, not plain text or Markdown')
    if '<!DOCTYPE' in raw.upper() or '<!ENTITY' in raw.upper():
        raise ValueError('DTD and entity declarations are not supported')
    root = ET.fromstring('<audit-root>' + raw + '</audit-root>')
    # Fetch ranges may have a transparent fragment wrapper. Never enter tables,
    # callouts or other containers: their headings belong to a different flow.
    if len(root) == 1 and root[0].tag == 'fragment':
        return list(root[0])
    if any(e.tag in ('fragment', 'excerpt') for e in root):
        raise ValueError('Use a full document or a single top-level fragment')
    return list(root)


def level(block):
    return int(block.tag[1:]) if re.fullmatch(r'h[1-9]', block.tag) else None


def blank(block):
    return (block.tag == 'p' and not ''.join(block.itertext()).strip()
            and all(e.tag in ('p', 'br', 'span', 'b', 'em', 'u') for e in block.iter()))


def audit(blocks, require_sibling_blank_line=False):
    active_levels = set()
    findings = []
    sibling_count = 0
    parent_child_count = 0
    for i, block in enumerate(blocks):
        depth = level(block)
        if depth is None:
            continue
        previous = i - 1
        gap = 0
        while previous >= 0 and blank(blocks[previous]):
            gap += 1
            previous -= 1
        prior_level = level(blocks[previous]) if previous >= 0 else None
        parent_child = prior_level is not None and prior_level < depth
        sibling = depth in active_levels
        codes = []
        if parent_child:
            parent_child_count += 1
            if gap or any(e.tag == 'hr' for e in blocks[max(previous, 0):i]):
                codes.append('parent_child_extra_gap')
        # Also catch a divider between otherwise adjacent parent/child headings.
        j = i - 1
        while j >= 0 and (blank(blocks[j]) or blocks[j].tag == 'hr'):
            j -= 1
        if j >= 0 and level(blocks[j]) is not None and level(blocks[j]) < depth:
            if any(e.tag == 'hr' for e in blocks[j+1:i]):
                codes.append('parent_child_divider')
        if sibling:
            sibling_count += 1
            if require_sibling_blank_line and gap == 0:
                codes.append('sibling_gap_missing')
            if gap > 1:
                codes.append('sibling_gap_excess')
        if codes:
            findings.append({'heading': ''.join(block.itertext()), 'block_id': block.get('id'),
                             'codes': codes, 'empty_blocks_before': gap})
        active_levels = {n for n in active_levels if n < depth}
        active_levels.add(depth)
    return {'status': 'fail' if findings else 'structure_pass_visual_pending',
            'profile': 'sibling_blank_line' if require_sibling_blank_line else 'native_spacing',
            'sibling_boundaries': sibling_count, 'parent_child_boundaries': parent_child_count,
            'findings': findings, 'visual_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='UTF-8 rich-text XML or Lark fetch JSON; not Markdown')
    parser.add_argument('--require-sibling-blank-line', action='store_true',
                        help='Use only when one empty block is the chosen h1–h9 sibling-gap mechanism')
    args = parser.parse_args()
    try:
        result = audit(load_blocks(Path(args.input).read_text()), args.require_sibling_blank_line)
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError) as exc:
        print(json.dumps({'status': 'invalid_input', 'error': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['findings'] else 0


if __name__ == '__main__':
    sys.exit(main())
