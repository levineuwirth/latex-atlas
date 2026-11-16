#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Real TeX/Poppler integration checks; outputs stay in build/ci/.

Run with python3 tools/ci_smoke.py after installing the README dependencies.
This exercises the public CLI in subprocesses, not mocked compiler calls.
"""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

from atlas_cli import NS, pdf_pages

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'build/ci'


def cli(*arguments, cwd=ROOT):
    print('+ atlas ' + ' '.join(map(str, arguments)), flush=True)
    subprocess.run([sys.executable, str(ROOT / 'atlas'), *map(str, arguments)],
                   cwd=cwd, check=True)


def checked_pdf(directory, expected_pages):
    report = json.loads((directory / 'check.json').read_text())
    assert report['findings'] == [], report
    assert report['pages'] == expected_pages, report
    pdf = directory / 'talk.pdf'
    assert len(pdf_pages(pdf)) == expected_pages, pdf
    return pdf


def notes_regressions(external, cwd):
    # Lists must share the narrow script column; large-font measurements must
    # not leak box warnings after a smaller, fitting size has been selected.
    fitting = (r'\mbox{An unbreakable phrase that is sized for the final font.} ' +
               'This is a sentence with a few words that should wrap nicely. ' * 7)
    (external / 'notes-regressions.tex').write_text(r'''
\documentclass[aspectratio=169]{beamer}
\usetheme{AtlasGrand}
\begin{document}
\begin{frame}{Numbered notes}Slide body.
\note[item]{This is a long list item which should stay in the note column without
running across the image of the slide. It should wrap neatly while rehearsing.}
\note[item]{Second list item that also belongs in the same narrow column.}
\end{frame}
{\AtlasGrandNight
\begin{frame}{Bulleted notes}Slide body.
\note{\begin{itemize}
\item These notes should be readable beside the thumbnail on a dark slide.
\item A second item with enough text to wrap in the note column.
\end{itemize}}
\end{frame}}
\begin{frame}{Fitting notes}Slide body.
\note{''' + fitting + r'''}
\end{frame}
\begin{frame}{\only<1>{First}\only<2>{Second} overlay}
One\pause Two
\note{An overlay-dependent title must agree with the slide.}
\end{frame}
\end{document}
''')
    for mode, count in [('script', 4), ('presenter', 5)]:
        cli('check', external / 'notes-regressions.tex', '--notes', mode,
            '--output-dir', OUT / 'external', cwd=cwd)
        pdf = checked_pdf(OUT / 'external/notes-regressions' / f'ornate-{mode}', count)
        if mode == 'presenter':
            # Check both halves, not just page counts: title tokens are evaluated
            # later than the slide and must retain the original overlay number.
            for page, expected, absent in zip(pdf_pages(pdf)[-2:],
                                              ['First', 'Second'], ['Second', 'First']):
                words = list(page.iter(NS + 'word'))
                midpoint = float(page.attrib['width']) / 2
                for right in (False, True):
                    text = [word.text for word in words
                            if (float(word.attrib['xMin']) >= midpoint) == right]
                    assert expected in text and absent not in text, text

    (external / 'statement-43.tex').write_text(r'''
\documentclass{beamer}
\usetheme{AtlasGrand}
\begin{document}
{\AtlasGrandQuiet
\begin{frame}[plain]
\AtlasGrandStatement{The finding}{My latest work could wait.}
{Almost everything requested was over a week old, including the complete set of comparison data.}
\end{frame}}
\end{document}
''')
    cli('check', external / 'statement-43.tex', '--output-dir', OUT / 'external', cwd=cwd)
    checked_pdf(OUT / 'external/statement-43/ornate', 1)

    # Do not hide actual overflow when suppressing the discarded measurements.
    (external / 'notes-overflow.tex').write_text(r'''
\documentclass[aspectratio=169]{beamer}
\usetheme{AtlasGrand}
\begin{document}
\begin{frame}{Too tall}Slide.\note{''' + 'A long sentence about an important subject. ' * 200 + r'''}
\end{frame}
\begin{frame}{Too wide}Slide.\note{\mbox{''' + 'Unbreakable text ' * 20 + r'''}}
\end{frame}
\end{document}
''')
    failed_check(external / 'notes-overflow.tex', '--notes', 'script', cwd=cwd)
    report = json.loads((OUT / 'external/notes-overflow/ornate-script/check.json').read_text())
    assert any('slide 1 is too long' in finding for finding in report['findings']), report
    assert any(r'Overfull \hbox' in finding for finding in report['findings']), report

    (external / 'draft-body.tex').write_text(
        '\\begin{frame}{Draft}\n\\AtlasTodo{same}\n\\AtlasTodo{same}\n\\end{frame}\n')
    (external / 'draft.tex').write_text(r'''
\documentclass{beamer}
\usetheme{AtlasGrand}
\begin{document}
\input{draft-body.tex}
\end{document}
''')
    failed_check(external / 'draft.tex', cwd=cwd)
    report = json.loads((OUT / 'external/draft/ornate/check.json').read_text())
    for line in (2, 3):
        assert any(f'draft-body.tex:{line}:1:' in item for item in report['findings']), report


def failed_check(source, *arguments, cwd, output=OUT / 'external'):
    command = [sys.executable, str(ROOT / 'atlas'), 'check', str(source),
               *arguments, '--output-dir', str(output)]
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    print(f'PASS: expected check failure for {source.name}', flush=True)
    return result.stdout


def size_pages(report):
    """Pages with small-text findings, asserting that nothing else was found."""
    findings = json.loads(report.read_text())['findings']
    assert all(' as projected ' in finding for finding in findings), findings
    return [int(finding.split(':')[0].split()[1]) for finding in findings]


def text_size_regressions(external, cwd):
    # A diagram shrunk into a column: its labels become unreadable in a room.
    (external / 'legibility.tex').write_text(r'''
\documentclass[aspectratio=169]{beamer}
\usetheme{AtlasGrand}
\begin{document}
\begin{frame}{Readable}Body text, and \tiny six-point text.\end{frame}
\begin{frame}{A shrunken diagram}
\resizebox{.12\linewidth}{!}{\begin{tikzpicture}
\node[draw] {their cluster}; \node[draw] at (3,0) {my cluster};
\end{tikzpicture}}
\end{frame}
\begin{frame}{An exhibit}\AtlasFinePrint{a document shown as an object}
\scalebox{.3}{A facsimile's small print.}
\end{frame}
\end{document}
''')
    stdout = failed_check(external / 'legibility.tex', cwd=cwd)
    report = OUT / 'external/legibility/ornate/check.json'
    assert size_pages(report) == [2], report.read_text()
    assert 'their cluster' in json.loads(report.read_text())['findings'][0]
    assert json.loads(report.read_text())['fine_print'] == [
        'Page 3: fine print by declaration (a document shown as an object)'], report.read_text()
    assert 'fine print by declaration' in stdout, stdout
    # A deck may set its own floor; the command line overrides the deck.
    cli('check', external / 'legibility.tex', '--min-text', '2',
        '--output-dir', OUT / 'external', cwd=cwd)
    source = (external / 'legibility.tex').read_text()
    (external / 'legibility.tex').write_text('% atlas: min-text=2\n' + source)
    cli('check', external / 'legibility.tex', '--output-dir', OUT / 'external', cwd=cwd)
    failed_check(external / 'legibility.tex', '--min-text', '6', cwd=cwd)


def emblem_and_photo(external, cwd):
    (external / 'mark.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
        '<circle cx="5" cy="5" r="4" fill="currentColor"/></svg>')
    cli('emblem', external / 'mark.svg', '--out-dir', external / 'assets', cwd=cwd)
    for palette, rgb in [('gold', b'\xd9\xb8\x79'), ('ink', b'\x29\x22\x1b'),
                         ('plain', b'\x00\x00\x00')]:
        # The disc's centre, rendered as a binary PPM, is exactly the palette colour.
        ppm = subprocess.run(['pdftoppm', '-r', '72', '-singlefile',
                              str(external / f'assets/mark-{palette}.pdf')],
                             check=True, capture_output=True).stdout
        _, width, height, _, pixels = ppm.split(maxsplit=4)
        centre = (int(height) // 2 * int(width) + int(width) // 2) * 3
        assert pixels[centre:centre + 3] == rgb, (palette, pixels[centre:centre + 3])

    # A phone photograph stored sideways, with location metadata.
    magick = shutil.which('magick') or shutil.which('convert')
    subprocess.run([magick, '-size', '300x200', 'gradient:red-blue', str(external / 'plain.jpg')],
                   check=True)
    jpeg = (external / 'plain.jpg').read_bytes()
    entries = [(0x0112, 3, 1, struct.pack('<HH', 6, 0)),      # Orientation: rotate 90° CW
               (0x8825, 4, 1, struct.pack('<I', 8 + 2 + 2 * 12 + 4))]  # GPS directory
    ifd = (struct.pack('<H', 2) + b''.join(struct.pack('<HHI', *entry[:3]) + entry[3]
                                           for entry in entries) + struct.pack('<I', 0))
    gps = struct.pack('<H', 1) + struct.pack('<HHI', 1, 2, 2) + b'N\0\0\0' + struct.pack('<I', 0)
    exif = b'Exif\0\0' + b'II*\0' + struct.pack('<I', 8) + ifd + gps
    (external / 'IMG 0001.jpg').write_bytes(jpeg[:2] + b'\xff\xe1' +
                                            struct.pack('>H', len(exif) + 2) + exif + jpeg[2:])
    cli('photo', external / 'IMG 0001.jpg', '--out-dir', external / 'assets', '--size', '250',
        cwd=cwd)
    prepared = external / 'assets/IMG 0001.jpg'
    size = subprocess.run([magick, 'identify', '-format', '%wx%h', str(prepared)] if
                          magick.endswith('magick') else
                          ['identify', '-format', '%wx%h', str(prepared)],
                          check=True, capture_output=True, text=True).stdout
    assert size == '167x250', size
    assert b'Exif' not in prepared.read_bytes()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='atlas-ci-') as directory:
        external = Path(directory) / 'External talk'
        cli('new', external, cwd=Path(directory))
        cli('check', external / 'talk.tex', '--all-variants',
            '--output-dir', OUT / 'external', cwd=Path(directory))
        for variant, count in [('ornate', 7), ('ornate-handout', 6),
                               ('plain', 7), ('plain-handout', 6)]:
            pdf = checked_pdf(OUT / 'external/talk' / variant, count)
            # Every variant also has a shareable name beside the variant folders.
            name = 'talk' + ('-' + variant.removeprefix('ornate-') if variant != 'ornate' else '')
            assert (OUT / f'external/talk/{name}.pdf').read_bytes() == pdf.read_bytes(), name
        # Speaker notes: a script page for every frame, slides from the handout;
        # a presenter view of every slide, double width with notes at the right.
        for mode, count in [('script', 6), ('presenter', 7)]:
            cli('check', external / 'talk.tex', '--notes', mode,
                '--output-dir', OUT / 'external', cwd=Path(directory))
            notes = checked_pdf(OUT / 'external/talk' / f'ornate-{mode}', count)
            page = pdf_pages(notes)[0]
            ratio = float(page.attrib['width']) / float(page.attrib['height'])
            assert (ratio > 3) == (mode == 'presenter'), (mode, ratio)
        pdf = OUT / 'external/talk/ornate/talk.pdf'
        cli('preview', pdf, '--pages', '1,3-7', cwd=Path(directory))
        overview = pdf.parent / 'talk-preview'
        manifest = json.loads((overview / 'manifest.json').read_text())
        assert manifest['pages'] == [1, 3, 4, 5, 6, 7], manifest
        assert len(list(overview.glob('page-*.png'))) == 6
        assert len(pdf_pages(overview / 'overview.pdf')) == 1

        # Real file includes, filenames with spaces, and forward references.
        shutil.copyfile(ROOT / 'presentations/crawler-assets/repository-targets.pdf',
                        external / 'assets/source graph.pdf')
        (external / 'body.tex').write_text(r'''
\begin{frame}{A local figure}
See frame~\ref{target}.
\includegraphics[width=.7\textwidth,height=.6\textheight,keepaspectratio]{assets/source graph.pdf}
\end{frame}
''')
        # The graph is shrunk to fit; this deck tests paths, so its floor is lower.
        (external / 'asset-talk.tex').write_text(r'''% atlas: min-text=1.5
\documentclass[aspectratio=169]{beamer}
\usetheme{Atlas}
\begin{document}
\input{body.tex}
\begin{frame}{Reference target}\label{target}A resolved reference.\end{frame}
\end{document}
''')
        cli('check', external / 'asset-talk.tex', '--output-dir', OUT / 'external',
            cwd=Path(directory))
        checked_pdf(OUT / 'external/asset-talk/ornate', 2)
        notes_regressions(external, Path(directory))
        text_size_regressions(external, Path(directory))
        emblem_and_photo(external, Path(directory))

    # Cover both themes, ordinary overlays, elaborate TikZ, and imported PDFs.
    # The specimens declare `% atlas: workdir=..`, so no --workdir is given.
    for name, handout, count in [('atlas', False, 17), ('atlas-grand', True, 19),
                                  ('atlas-euler', True, 12)]:
        arguments = ['check', ROOT / 'presentations' / (name + '.tex'),
                     '--output-dir', OUT / 'specimens']
        if handout:
            arguments.append('--handout')
        cli(*arguments)
        variant = 'ornate-handout' if handout else 'ornate'
        checked_pdf(OUT / 'specimens' / name / variant, count)

    # The Crawler deck shows the essay's own charts, whose labels are too
    # small to read in a room: the check must find exactly those pages,
    # and accept the declared facsimile of the petition.
    crawler_source = ROOT / 'presentations/crawler-chronicles.tex'
    failed_check(crawler_source, cwd=ROOT, output=OUT / 'specimens')
    report = OUT / 'specimens/crawler-chronicles/ornate/check.json'
    assert size_pages(report) == [16, 20, 25, 26, 29, 30], report.read_text()
    assert json.loads(report.read_text())['pages'] == 37
    assert [note.split(':')[0] for note in json.loads(report.read_text())['fine_print']] == [
        'Page 33'], report.read_text()

    # A real script: every frame, including those without notes and the
    # full-page figures whose thumbnails come from the handout. Its text
    # sizes are the handout's, so its pages are numbered as the script's.
    failed_check(crawler_source, '--notes', 'script', cwd=ROOT, output=OUT / 'specimens')
    report = OUT / 'specimens/crawler-chronicles/ornate-script/check.json'
    assert size_pages(report) == [15, 18, 22, 23, 26, 27], report.read_text()
    assert json.loads(report.read_text())['pages'] == 34

    # A long deck must make multiple overview sheets, preserving every page.
    crawler = OUT / 'specimens/crawler-chronicles/ornate/talk.pdf'
    cli('preview', crawler)
    preview = crawler.parent / 'talk-preview'
    manifest = json.loads((preview / 'manifest.json').read_text())
    assert manifest['pages'] == list(range(1, 38)), manifest
    assert len(list(preview.glob('page-*.png'))) == 37
    assert len(pdf_pages(preview / 'overview.pdf')) == 5
    print('PASS: external starter, notes, text sizes, imports, relative assets, all specimens, '
          'and multipage previews.', flush=True)


if __name__ == '__main__':
    main()
