import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'document-master/scripts/check_heading_spacing.py'
spec = importlib.util.spec_from_file_location('spacing', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class HeadingSpacing(unittest.TestCase):
    def check(self, xml, required=True):
        return m.audit(m.load_blocks(xml), required)

    def test_bulk_empty_removal_regresses_siblings(self):
        good = '<h1>方案</h1><h2>总览</h2><table/><p/><h2>实施</h2><p>内容</p>'
        self.assertFalse(self.check(good)['findings'])
        bad = self.check(good.replace('<p/>', ''))
        self.assertEqual(bad['findings'][0]['codes'], ['sibling_gap_missing'])

    def test_parent_child_gap_is_a_separate_failure(self):
        r = self.check('<h1>方案</h1><p/><h2>总览</h2><p>内容</p><p/><h2>实施</h2>')
        self.assertEqual(r['findings'][0]['codes'], ['parent_child_extra_gap'])

    def test_parent_divider(self):
        self.assertIn('parent_child_divider', self.check('<h1>方案</h1><hr/><h2>总览</h2>')['findings'][0]['codes'])

    def test_nested_and_new_chapter_reset(self):
        xml = '<h1>A</h1><h2>A1</h2><p>说明</p><h3>A11</h3><p>内容</p><p/><h3>A12</h3><p>内容</p><p/><h2>A2</h2><p>本节内容</p><p/><h1>B</h1><h2>B1</h2>'
        r=self.check(xml)
        self.assertFalse(r['findings']);self.assertEqual(r['sibling_boundaries'],3)

    def test_container_content_does_not_pollute_hierarchy(self):
        r=self.check('<h1>A</h1><h2>A1</h2><table><tr><td><h2>单元格</h2></td></tr></table><p/><h2>A2</h2>')
        self.assertFalse(r['findings']);self.assertEqual(r['sibling_boundaries'],1)

    def test_multiple_blanks_are_not_better(self):
        self.assertEqual(self.check('<h1>A</h1><h2>A1</h2><p>内容</p><p/><p/><h2>A2</h2>')['findings'][0]['codes'],['sibling_gap_excess'])

    def test_native_gap_is_not_forced_to_empty_blocks(self):
        r=self.check('<h1>A</h1><h2>A1</h2><p>内容</p><h2>A2</h2>',False)
        self.assertFalse(r['findings']);self.assertFalse(r['visual_verified'])

    def test_whitespace_and_resources(self):
        self.assertTrue(m.blank(m.load_blocks('<p><span> </span><br/></p>')[0]))
        self.assertFalse(m.blank(m.load_blocks('<p><img src="example"/></p>')[0]))

    def test_image_boundary_needs_sibling_gap(self):
        r=self.check('<h1>A</h1><h2>A1</h2><img src="example"/><h2>A2</h2>')
        self.assertEqual(r["findings"][0]["codes"],["sibling_gap_missing"])

    def test_major_chapters_also_require_gap(self):
        xml = '<title>文档名</title><h1>一</h1><h2>1.1</h2><p>正文</p><h1>二</h1><h2>2.1</h2><table/><h1>三</h1>'
        r = self.check(xml)
        self.assertEqual([f['heading'] for f in r['findings']], ['二', '三'])
        self.assertTrue(all(f['codes'] == ['sibling_gap_missing'] for f in r['findings']))
        good = xml.replace('<h1>二', '<p/><h1>二').replace('<h1>三', '<p/><h1>三')
        self.assertFalse(self.check(good)['findings'])

    def test_plain_text_is_not_a_structure_pass(self):
        for text in ('', '## 标题', '正文'):
            with self.assertRaises(ValueError): m.load_blocks(text)

    def test_fetch_json(self):
        import json
        self.assertFalse(self.check(json.dumps({"data":{"document":{"content":"<h1>A</h1><h2>A1</h2>"}}}))["findings"])

    def test_entity_declaration_rejected(self):
        with self.assertRaises(ValueError):m.load_blocks('<!DOCTYPE r><h1>A</h1>')

    def test_range_requires_context(self):
        self.assertEqual(self.check('<fragment><h1>A</h1><h2>A1</h2></fragment>')['status'],'structure_pass_visual_pending')
        with self.assertRaises(ValueError):m.load_blocks('<excerpt/>')

if __name__=='__main__':unittest.main()
