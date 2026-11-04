#!/usr/bin/env python3
"""Read-only review hints for rich-text XML or a full Lark fetch JSON.

Flags style differences and common editorial notes. Findings need human review.
Does not establish factual accuracy, image relevance or visual acceptance.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from check_heading_spacing import load_blocks


PROCESS_NOTE = re.compile(r'尚未取得.{0,12}截图|暂未取得.{0,12}截图|待补回放截图|已检查全部章节|本轮(?:修改|审校)|按.{0,16}规范改写')
CIRCLED_NUMBER = re.compile(r'[①-⑳❶-❿]')


def cell_style(cell):
    """Keep native style values. Different values require review, not conversion."""
    background = re.sub(r'\s+', '', cell.get('background-color', 'none')).lower()
    text = ''.join(cell.itertext()).strip()
    bold_text = ''.join(''.join(node.itertext()) for node in cell.iter('b')).strip()
    return background, bool(text) and text == bold_text


def audit(blocks):
    root = ET.Element('review-root')
    root.extend(blocks)
    if root.find('.//excerpt') is not None:
        raise ValueError('Use a complete document or section, not table excerpts')
    findings = []
    headers = []
    for number, table in enumerate(root.iter('table'), 1):
        cells = table.findall('./thead/tr/th')
        if not cells:
            continue
        styles = [cell_style(cell) for cell in cells]
        location = {'table': number, 'block_id': table.get('id')}
        if len(set(styles)) > 1:
            findings.append(dict(location, code='header_cells_differ'))
        headers.append((location, tuple(styles)))
    uniform_headers = [styles[0] for _, styles in headers if len(set(styles)) == 1]
    if uniform_headers:
        common = Counter(uniform_headers).most_common(1)[0][0]
        for location, styles in headers:
            if len(set(styles)) == 1 and styles[0] != common:
                findings.append(dict(location, code='table_header_style_differs',
                                     observed=list(styles[0]), common=list(common)))
    for node in root.iter():
        if node.tag not in ('p', 'li'):
            continue
        # Inspect each paragraph once when nested lists contain paragraphs.
        if node.tag == 'li' and node.find('.//p') is not None:
            continue
        text = ''.join(node.itertext()).strip()
        codes = []
        if PROCESS_NOTE.search(text):
            codes.append('possible_editorial_process_note')
        if CIRCLED_NUMBER.search(text):
            codes.append('circled_number')
        if codes:
            findings.append({'block_id': node.get('id'), 'codes': codes, 'text': text[:180]})
    return {'status': 'review_required' if findings else 'static_pass_review_pending',
            'header_tables_checked': len(headers), 'findings': findings,
            'semantic_verified': False, 'visual_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='UTF-8 rich-text XML or Lark fetch JSON')
    args = parser.parse_args()
    try:
        result = audit(load_blocks(Path(args.input).read_text()))
    except (ValueError, KeyError, TypeError, OSError, ET.ParseError) as error:
        print(json.dumps({'status': 'invalid_input', 'error': str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['findings'] else 0


if __name__ == '__main__':
    sys.exit(main())
