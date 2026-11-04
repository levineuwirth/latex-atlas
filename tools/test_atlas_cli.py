# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Fast CLI regression checks; real TeX/Poppler smoke tests are documented separately."""
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import atlas_cli as atlas


def page(text='A slide', x=12, y=12):
    element = ET.Element(atlas.NS + 'page', width='160', height='90')
    ET.SubElement(element, atlas.NS + 'word', xMin=str(x), yMin=str(y),
                  xMax=str(x + 40), yMax=str(y + 10)).text = text
    return element


class WorkflowTests(unittest.TestCase):
    def test_new_refuses_to_overwrite_a_talk(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            destination = Path(temp) / 'Talk with spaces'
            atlas.new_talk(destination)
            self.assertTrue((destination / 'assets').is_dir())
            self.assertIn('atlas build talk.tex', (destination / 'talk.tex').read_text())
            (destination / 'talk.tex').write_text('My edits')
            with self.assertRaisesRegex(atlas.AtlasError, 'already exists'):
                atlas.new_talk(destination)
            self.assertEqual((destination / 'talk.tex').read_text(), 'My edits')

    def test_page_selection_preserves_order_and_removes_duplicates(self):
        pages = [page(str(i)) for i in range(6)]
        self.assertEqual(atlas.select_pages(pages, '6,2-4,2'), [6, 2, 3, 4])
        self.assertEqual(atlas.select_pages(pages), [1, 2, 3, 4, 5, 6])

    def test_bad_page_ranges_are_errors(self):
        for value in ['0', '7', '4-2', '1,', 'one', '-1']:
            with self.subTest(value=value), self.assertRaises(atlas.AtlasError):
                atlas.select_pages([page()] * 6, value)

    def test_text_selection_rejects_ambiguous_overlays(self):
        pages = [page('First overlay'), page('First overlay'), page('Conclusion')]
        self.assertEqual(atlas.select_pages(pages, phrases=['Conclusion']), [3])
        for phrase in ['First overlay', 'Absent', '']:
            with self.subTest(phrase=phrase), self.assertRaises(atlas.AtlasError):
                atlas.select_pages(pages, phrases=[phrase])

    def test_bounds_include_off_page_and_near_edge_words(self):
        self.assertEqual(atlas.boundary_findings([page()]), [])
        findings = atlas.boundary_findings([page('off left', x=-2), page('off bottom', y=85), page('near edge', x=.5)])
        self.assertEqual(len(findings), 3)
        self.assertIn('Page 2', findings[1])

    def test_log_warnings_missing_glyphs_and_overflow(self):
        log = ('Normal compilation output\n'
               'LaTeX Warning: Reference `missing` undefined.\n'
               'Overfull \\hbox (5.0pt too wide) in paragraph\n'
               'Underfull \\vbox (badness 10000)\n'
               'Missing character: There is no X in font Y!\n')
        self.assertEqual(len(atlas.log_findings(log)), 4)
        self.assertEqual(atlas.log_findings('Output written on talk.pdf (7 pages).'), [])

    def test_missing_dependency_is_actionable(self):
        with patch.object(atlas.shutil, 'which', return_value=None):
            with self.assertRaisesRegex(atlas.AtlasError, 'Missing programs: latexmk'):
                atlas.require('latexmk')

    def test_build_failure_does_not_preview_an_old_pdf(self):
        with patch.object(atlas, 'require'), patch.object(atlas, 'build', side_effect=atlas.AtlasError('broken TeX')), \
             patch.object(atlas, 'preview') as preview, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(atlas.main(['preview', 'talk.tex']), 1)
            preview.assert_not_called()

    def test_build_uses_deck_directory_and_separate_variants(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            source = Path(temp) / 'Talk with spaces.tex'
            source.write_text('source')
            calls = []

            def fake_run(command, cwd, log, env):
                calls.append((command, cwd, log, env))
                (log.parent / 'talk.pdf').touch()

            with patch.object(atlas, 'require'), patch.object(atlas.subprocess, 'run',
                    return_value=subprocess.CompletedProcess([], 0, stdout='/tex/package.sty\n')), \
                 patch.object(atlas, 'run_logged', side_effect=fake_run):
                ornate = atlas.build(source)
                plain = atlas.build(source, plain=True, handout=True)
                report = ornate.parent / 'check.json'
                report.write_text('{"findings": []}')
                atlas.build(source, force=True)
                self.assertFalse(report.exists(), 'A rebuild must invalidate the previous check report')
            self.assertNotEqual(ornate, plain)
            self.assertEqual(calls[0][1], source.parent)
            self.assertIn(str(atlas.ROOT / 'sty'), calls[0][3]['TEXINPUTS'])
            self.assertIn('-g', calls[2][0])
            driver = (plain.parent / 'atlas-driver.tex').read_text()
            self.assertIn(r'\PassOptionsToClass{handout}{beamer}', driver)
            self.assertIn(r'\PassOptionsToPackage{plain}', driver)
            self.assertIn(str(source), driver)

    def test_pdf_mode_rejects_ineffective_build_flags(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(atlas.main(['preview', 'talk.pdf', '--handout']), 1)

    def test_poppler_control_character_keeps_its_bounding_box(self):
        output = ('<html xmlns="http://www.w3.org/1999/xhtml"><body>'
                  '<page width="160" height="90"><word xMin="-2" yMin="2" '
                  'xMax="3" yMax="10">\x07</word></page></body></html>')
        with patch.object(atlas, 'require'), patch.object(atlas.subprocess, 'run',
                return_value=subprocess.CompletedProcess([], 0, stdout=output, stderr='')):
            pages = atlas.pdf_pages(Path('talk.pdf'))
            self.assertEqual(len(atlas.boundary_findings(pages)), 1)


if __name__ == '__main__':
    unittest.main()
