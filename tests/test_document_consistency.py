import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'document-master' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import check_document_consistency as consistency
from check_heading_spacing import load_blocks


def table(color, bold=True):
    text = '<b>状态</b>' if bold else '状态'
    return f'<table><thead><tr><th background-color="{color}"><p>{text}</p></th></tr></thead><tbody><tr><td>正常</td></tr></tbody></table>'


class DocumentConsistency(unittest.TestCase):
    def audit(self, text):
        return consistency.audit(load_blocks(text))

    def test_mixed_background_is_reported(self):
        report = self.audit(table('gray') + table('blue'))
        self.assertEqual(report['findings'][0]['code'], 'table_header_style_differs')

    def test_missing_bold_is_reported(self):
        report = self.audit(table('gray') + table('gray', bold=False))
        self.assertEqual(report['findings'][0]['code'], 'table_header_style_differs')

    def test_mixed_cells_are_reported(self):
        report = self.audit('<table><thead><tr><th><b>A</b></th><th>B</th></tr></thead></table>')
        self.assertEqual(report['findings'][0]['code'], 'header_cells_differ')

    def test_consistent_uncolored_headers_are_allowed(self):
        self.assertFalse(self.audit(table('none') + table('none'))['findings'])

    def test_editorial_note_inside_table_is_found(self):
        report = self.audit('<table><tr><td><p id="note">尚未取得该路径的独立截图</p></td></tr></table>')
        self.assertEqual(report['findings'][0]['block_id'], 'note')

    def test_business_uncertainty_is_preserved(self):
        report = self.audit('<p>根因待查，线上版本适用性待核实。实验显示内存增加，容量尚未验证。</p>')
        self.assertFalse(report['findings'])

    def test_circled_number_is_found(self):
        self.assertEqual(self.audit('<p>①检查输入</p>')['findings'][0]['codes'], ['circled_number'])

    def test_regular_ordered_list_is_allowed(self):
        self.assertFalse(self.audit('<ol><li seq="1">检查输入</li></ol>')['findings'])

    def test_pass_does_not_claim_semantic_or_visual_acceptance(self):
        result = self.audit('<p>故障现象与预期行为</p>')
        self.assertFalse(result['semantic_verified'])
        self.assertFalse(result['visual_verified'])

    def test_excerpt_is_not_full_document_acceptance(self):
        with self.assertRaises(ValueError):
            self.audit('<fragment><excerpt><table/></excerpt></fragment>')


if __name__ == '__main__':
    unittest.main()
