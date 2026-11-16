# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Fast CLI regression checks; real TeX/Poppler smoke tests are documented separately."""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import atlas_cli as atlas


def segment(marker, body):
    return bytes([0xFF, marker]) + (len(body) + 2).to_bytes(2, 'big') + body


KEEP = [segment(0xE0, b'JFIF\0\1\1'), segment(0xE2, b'ICC_PROFILE\0\1\1icc'),
        segment(0xDB, b'tables'), segment(0xEE, b'Adobe\0d')]
DROP = [segment(0xFE, b'GPS 41.8N, camera X'), segment(0xE1, b'Exif\0\0II*'),
        segment(0xE1, b'http://ns.adobe.com/xap/1.0/\0<x/>'), segment(0xED, b'Photoshop 3.0\0'),
        segment(0xE2, b'MPF\0'), segment(0xE0, b'JFXX\0')]
SCAN = b'\xff\xda' + b'\0\x08scan' + b'\xff\xfe not a comment inside data \xff\xd9'
JPEG = b'\xff\xd8' + KEEP[0] + DROP[0] + DROP[1] + KEEP[1] + DROP[2] + KEEP[2] + b''.join(DROP[3:]) + KEEP[3] + SCAN
CLEAN_JPEG = b'\xff\xd8' + b''.join(KEEP) + SCAN


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
            self.assertIn('Permission is hereby granted', (destination / 'LICENSE-ATLAS').read_text())
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

    def test_todo_locations_skip_comments_literals_and_longer_commands(self):
        source = (r'% \AtlasTodo{comment}' '\n'
                  r'\verb|\AtlasTodo{example}| \string\AtlasTodo' '\n'
                  r'\begin{verbatim}' '\n' r'\AtlasTodo{example}' '\n'
                  r'\end{verbatim}' '\n'
                  r'\AtlasTodoExtra{not a marker}' '\n'
                  r'\% \AtlasTodo{first} \AtlasTodo{second}' '\n'
                  r'\\% \AtlasTodo{comment after a line break}' '\n')
        self.assertEqual(list(atlas.todo_positions(source)), [(7, 4), (7, 22)])

    def test_todo_examples_in_literal_commands_are_not_draft_markers(self):
        source = (r'\string \AtlasTodo \verb*+\AtlasTodo{example}+' '\n'
                  r'\lstinline[language=tex]|\AtlasTodo{example}|' '\n'
                  r'\detokenize{\AtlasTodo{nested {example}} \{ \}}' '\n'
                  r'\AtlasTodo{real}')
        self.assertEqual(list(atlas.todo_positions(source)), [(4, 1)])

    def test_todo_recorder_finds_included_sources_once_with_exact_locations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            body = root / 'included body.tex'
            body.write_text('\\begin{frame}{Draft}\n\\AtlasTodo{same}\n'
                            '\\AtlasTodo{same}\n\\end{frame}\n')
            (root / 'unread.tex').write_text(r'\AtlasTodo{not included}')
            pdf = root / 'talk.pdf'
            pdf.with_suffix('.fls').write_text(
                f'PWD {root}\nINPUT included body.tex\nINPUT {body}\n')
            self.assertEqual(atlas.todo_findings(pdf), [
                f'{body}:2:1: Unfinished (\\AtlasTodo)',
                f'{body}:3:1: Unfinished (\\AtlasTodo)'])

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

    def fake_builds(self, temp, pages=None):
        """Patch the compiler; each build writes a PDF and a log with a page count."""
        source = Path(temp) / 'Talk with spaces.tex'
        source.write_text('source')
        calls = []

        def fake_run(command, cwd, log, env):
            calls.append(command)
            variant = log.parent.name
            (log.parent / 'talk.pdf').touch()
            count = (pages or {}).get(variant, 6)
            (log.parent / 'talk.log').write_text(f'Output written on talk.pdf ({count} pages, 1 bytes).')

        patches = [patch.object(atlas, 'require'),
                   patch.object(atlas.subprocess, 'run', return_value=subprocess.CompletedProcess(
                       [], 0, stdout='/tex/package.sty\n')),
                   patch.object(atlas, 'run_logged', side_effect=fake_run)]
        return source, calls, patches

    def test_presenter_notes_are_a_separate_variant(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            source, calls, patches = self.fake_builds(temp)
            with patches[0], patches[1], patches[2]:
                pdf = atlas.build(source, notes='presenter')
            self.assertEqual(pdf.parent.name, 'ornate-presenter')
            driver = (pdf.parent / 'atlas-driver.tex').read_text()
            self.assertIn(r'\def\AtlasNotesMode{presenter}', driver)
            self.assertNotIn('handout', driver)
            self.assertEqual(len(calls), 1)

    def test_script_notes_build_the_handout_for_their_slides(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            source, calls, patches = self.fake_builds(temp)
            with patches[0], patches[1], patches[2]:
                pdf = atlas.build(source, plain=True, notes='script')
            self.assertEqual(pdf.parent.name, 'plain-script')
            self.assertEqual(len(calls), 2, 'the handout is built first')
            self.assertTrue(str(calls[0][-1]).endswith('plain-handout/atlas-driver.tex'))
            driver = (pdf.parent / 'atlas-driver.tex').read_text()
            handout = pdf.parent.parent / 'plain-handout'
            self.assertIn(r'\PassOptionsToClass{handout}{beamer}', driver)
            self.assertIn(r'\def\AtlasNotesMode{script}', driver)
            self.assertIn(str(handout / 'talk.pdf'), driver)
            self.assertIn(str(handout / 'talk.aux'), driver)

    def test_script_must_match_the_handout_page_for_page(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            source, _, patches = self.fake_builds(temp, {'ornate-script': 5})
            with patches[0], patches[1], patches[2]:
                with self.assertRaisesRegex(atlas.AtlasError, '5 pages but the handout has 6'):
                    atlas.build(source, notes='script')

    def test_notes_option_conflicts_are_errors(self):
        with self.assertRaisesRegex(atlas.AtlasError, 'omit --handout'):
            atlas.build(Path('talk.tex'), handout=True, notes='script')
        with self.assertRaisesRegex(atlas.AtlasError, 'Unknown notes mode'):
            atlas.build(Path('talk.tex'), notes='both')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(atlas.main(['check', 'talk.tex', '--all-variants', '--notes', 'script']), 1)
            self.assertEqual(atlas.main(['preview', 'talk.pdf', '--notes', 'presenter']), 1)

    def test_page_count_comes_from_the_log(self):
        with tempfile.TemporaryDirectory() as temp:
            pdf = Path(temp) / 'talk.pdf'
            pdf.with_suffix('.log').write_text('Output written on /a long/\npath/talk.pdf (34 pages, 9 bytes).')
            self.assertEqual(atlas.log_page_count(pdf), 34)
            pdf.with_suffix('.log').write_text('No pages of output.')
            with self.assertRaises(atlas.AtlasError):
                atlas.log_page_count(pdf)

    def test_deck_settings_are_read_from_the_top_comment(self):
        with tempfile.TemporaryDirectory() as temp:
            deck = Path(temp) / 'talks' / 'one' / 'talk.tex'
            deck.parent.mkdir(parents=True)
            deck.write_text('%!TEX program = lualatex\n'
                            "% atlas: workdir='../..' min-text=5.5\n\\documentclass{beamer}\n")
            settings = atlas.deck_settings(deck)
            self.assertEqual(settings['workdir'], deck.parent / '../..')
            self.assertEqual(settings['min-text'], 5.5)
            deck.write_text('\\documentclass{beamer}\n')
            self.assertEqual(atlas.deck_settings(deck), {})
            for bad in ['% atlas: workdir', '% atlas: colour=red', '% atlas: min-text=tiny',
                        "% atlas: workdir='open"]:
                deck.write_text(bad + '\n')
                with self.subTest(bad=bad), self.assertRaises(atlas.AtlasError):
                    atlas.deck_settings(deck)

    def test_deck_workdir_applies_unless_the_command_line_overrides_it(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            source, calls, patches = self.fake_builds(temp)
            source.write_text('% atlas: workdir=..\n')
            cwds = []
            with patches[0], patches[1], patch.object(
                    atlas, 'run_logged', side_effect=lambda command, cwd, log, env: (
                        cwds.append(cwd), (log.parent / 'talk.pdf').touch())):
                atlas.build(source)
                atlas.build(source, workdir=Path(temp))
            self.assertEqual(cwds, [Path(temp).parent.resolve(), Path(temp).resolve()])

    def test_each_variant_gets_a_shareable_name(self):
        for variant, name in [('ornate', 'deck.pdf'), ('ornate-handout', 'deck-handout.pdf'),
                              ('plain-handout', 'deck-plain-handout.pdf'),
                              ('ornate-presenter', 'deck-presenter.pdf')]:
            pdf = Path('/b/deck') / variant / 'talk.pdf'
            self.assertEqual(atlas.named_pdf(pdf), Path('/b/deck') / name)
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            source, _, patches = self.fake_builds(temp)
            with patches[0], patches[1], patches[2]:
                pdf = atlas.build(source, plain=True)
            self.assertTrue((pdf.parent.parent / 'Talk with spaces-plain.pdf').is_file())

    def test_a_bare_name_in_the_checkout_becomes_a_personal_talk(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temp).resolve()
            (root / 'presentations').mkdir()
            (root / 'presentations/starter.tex').write_text('starter')
            (root / 'LICENSE').write_text('MIT License\nterms')
            previous = Path.cwd()
            os.chdir(root)
            try:
                with patch.object(atlas, 'ROOT', root):
                    atlas.new_talk(Path('keynote'))
                    atlas.new_talk(Path('elsewhere/keynote'))
            finally:
                os.chdir(previous)
            self.assertTrue((root / 'talks/keynote/talk.tex').is_file())
            self.assertTrue((root / 'elsewhere/keynote/talk.tex').is_file())

    def test_fine_print_declarations_survive_log_wrapping(self):
        log = ('Atlas fine print on page 2 (a court filing shown as an exhibit, wrapped by Te\n'
               'X at seventy-nine columns)\nAtlas fine print on page 12 (seal)\n')
        self.assertEqual(atlas.fine_print_pages(log), {
            2: 'a court filing shown as an exhibit, wrapped by TeX at seventy-nine columns',
            12: 'seal'})

    def test_small_text_is_reported_once_per_page_unless_declared(self):
        box = (10, 10, 30, 6, 1360, 765)
        runs = [(1, 11.0, 'Body', box), (1, 4.0, 'axis', box), (1, 3.0, 'tick', box),
                (2, 5.9, 'rounded', box), (3, 2.3, 'engraving', box), (4, 5.0, 'legend', box),
                (5, 4.0, 'cropped', box)]
        rendered = []

        def inked(pdf, number, page_runs):
            rendered.append(number)
            return [] if number == 5 else page_runs
        with patch.object(atlas, 'text_sizes', return_value=runs), \
             patch.object(atlas, 'inked_runs', side_effect=inked):
            findings, waived = atlas.text_size_findings(Path('talk.pdf'), 6, {3: 'ornament'})
        self.assertEqual(len(findings), 2)
        self.assertIn('Page 1: 2 text runs below 6 pt', findings[0])
        self.assertIn("smallest 3.0 pt): 'tick', 'axis'", findings[0])
        self.assertIn('Page 4: 1 text run below', findings[1])
        self.assertEqual(waived, ['Page 3: fine print by declaration (ornament)'])
        self.assertEqual(rendered, [1, 4, 5])  # Only pages that could fail are rendered.

    def test_only_runs_that_leave_ink_count(self):
        # A 100 x 50 pixel page: text drew a mark near the first run only.
        bare = bytes(100 * 50)
        inked = bytearray(bare)
        inked[20 * 100 + 12] = 200
        page = (200, 100)  # pdftohtml units, twice the pixel size
        shown, hidden = [(3.0, 'shown', (20, 38, 10, 4) + page),
                         (3.0, 'hidden', (150, 60, 20, 4) + page)]
        renders = {(): (100, 50, bytes(inked)), ('-dFILTERTEXT',): (100, 50, bare)}
        with patch.object(atlas.shutil, 'which', return_value='/usr/bin/gs'), \
             patch.object(atlas, 'gray_page', side_effect=lambda pdf, n, r, *o: renders[o]):
            self.assertEqual(atlas.inked_runs(Path('talk.pdf'), 1, [shown, hidden]), [shown])
            # When filtering text changes nothing at all, keep every run.
            renders[()] = (100, 50, bare)
            self.assertEqual(atlas.inked_runs(Path('talk.pdf'), 1, [shown, hidden]), [shown, hidden])
        with patch.object(atlas.shutil, 'which', return_value=None):
            self.assertEqual(atlas.inked_runs(Path('talk.pdf'), 1, [hidden]), [hidden])

    def test_emblem_recolours_only_marked_colours(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            svg = Path(temp) / 'mark.svg'
            svg.write_text('<svg><path fill="currentColor" stroke="#123456"/></svg>')
            written = {}

            def fake_rsvg(command, cwd, log, env=None):
                written[Path(command[4]).name] = Path(command[5]).read_text()
            with patch.object(atlas, 'require'), patch.object(atlas, 'run_logged', side_effect=fake_rsvg):
                atlas.emblem(svg, name='seal')
                self.assertEqual(sorted(written), ['seal-gold.pdf', 'seal-ink.pdf', 'seal-plain.pdf'])
                self.assertIn('fill="#D9B879" stroke="#123456"', written['seal-gold.pdf'])
                svg.write_text('<svg><path fill="#000000"/></svg>')
                with self.assertRaisesRegex(atlas.AtlasError, '--replace'):
                    atlas.emblem(svg)
                atlas.emblem(svg, colors=['#000000'])
                self.assertIn('fill="#29221B"', written['mark-ink.pdf'])
                # Colour names in selectors, classes, ids, and text stay as written.
                svg.write_text('<svg><style>.black{fill:black} #black { stroke : Black ; }</style>'
                               '<path class="black" id="black" style="fill:#000;stroke:black"/>'
                               '<text fill="BLACK">black</text></svg>')
                atlas.emblem(svg, colors=['black'])
                self.assertEqual(written['mark-gold.pdf'],
                                 '<svg><style>.black{fill:#D9B879} #black { stroke : #D9B879 ; }</style>'
                                 '<path class="black" id="black" style="fill:#000;stroke:#D9B879"/>'
                                 '<text fill="#D9B879">black</text></svg>')
                svg.write_text('<svg><path class="black" d="M0 0"/></svg>')
                with self.assertRaisesRegex(atlas.AtlasError, '--replace'):
                    atlas.emblem(svg, colors=['black'])

    def test_photo_never_replaces_originals_or_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temp)
            original = root / 'site.jpg'
            original.write_bytes(b'jpeg')
            with patch.object(atlas.shutil, 'which', return_value='/usr/bin/magick'), \
                 patch.object(atlas, 'run_logged') as run:
                with self.assertRaisesRegex(atlas.AtlasError, 'original'):
                    atlas.photo([original], root)
                (root / 'out').mkdir()
                (root / 'out/site.jpg').write_bytes(b'old')
                with self.assertRaisesRegex(atlas.AtlasError, '--force'):
                    atlas.photo([original], root / 'out')
                (root / 'b').mkdir()
                (root / 'b/site.png').write_bytes(b'png')
                with self.assertRaisesRegex(atlas.AtlasError, 'same output name'):
                    atlas.photo([original, root / 'b/site.png'], root / 'new')
                run.assert_not_called()
                run.side_effect = lambda command, cwd, log: Path(command[-1]).write_bytes(JPEG)
                atlas.photo([original], root / 'out', force=True)
                command = run.call_args[0][0]
                self.assertIn('-auto-orient', command)
                self.assertIn('!icc,*', command)
            self.assertEqual((root / 'out/site.jpg').read_bytes(), CLEAN_JPEG)
            self.assertEqual(original.read_bytes(), b'jpeg')

    def test_jpeg_keeps_only_decoding_segments(self):
        self.assertEqual(atlas.jpeg_without_metadata(JPEG), CLEAN_JPEG)
        with self.assertRaisesRegex(atlas.AtlasError, 'did not write a JPEG'):
            atlas.jpeg_without_metadata(b'\x89PNG')
        with self.assertRaisesRegex(atlas.AtlasError, 'cannot read'):
            atlas.jpeg_without_metadata(JPEG[:30])

    def test_text_size_options_are_validated(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(atlas.main(['check', 'talk.tex', '--min-text', '0']), 1)
            self.assertEqual(atlas.main(['photo', 'a.jpg', '--size', '20']), 1)

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
