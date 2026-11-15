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


def failed_check(source, *arguments, cwd):
    command = [sys.executable, str(ROOT / 'atlas'), 'check', str(source),
               *arguments, '--output-dir', str(OUT / 'external')]
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    print(f'PASS: expected check failure for {source.name}', flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='atlas-ci-') as directory:
        external = Path(directory) / 'External talk'
        cli('new', external, cwd=Path(directory))
        cli('check', external / 'talk.tex', '--all-variants',
            '--output-dir', OUT / 'external', cwd=Path(directory))
        for variant, count in [('ornate', 7), ('ornate-handout', 6),
                               ('plain', 7), ('plain-handout', 6)]:
            checked_pdf(OUT / 'external/talk' / variant, count)
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
        (external / 'asset-talk.tex').write_text(r'''
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

    # Cover both themes, ordinary overlays, elaborate TikZ, and imported PDFs.
    for name, handout, count in [('atlas', False, 17), ('atlas-grand', True, 19),
                                  ('atlas-euler', True, 12), ('crawler-chronicles', False, 37)]:
        arguments = ['check', ROOT / 'presentations' / (name + '.tex'),
                     '--workdir', ROOT, '--output-dir', OUT / 'specimens']
        if handout:
            arguments.append('--handout')
        cli(*arguments)
        variant = 'ornate-handout' if handout else 'ornate'
        checked_pdf(OUT / 'specimens' / name / variant, count)

    # A real script: every frame, including those without notes and the
    # full-page figures whose thumbnails come from the handout.
    cli('check', ROOT / 'presentations/crawler-chronicles.tex', '--notes', 'script',
        '--workdir', ROOT, '--output-dir', OUT / 'specimens')
    checked_pdf(OUT / 'specimens/crawler-chronicles/ornate-script', 34)

    # A long deck must make multiple overview sheets, preserving every page.
    crawler = OUT / 'specimens/crawler-chronicles/ornate/talk.pdf'
    cli('preview', crawler)
    preview = crawler.parent / 'talk-preview'
    manifest = json.loads((preview / 'manifest.json').read_text())
    assert manifest['pages'] == list(range(1, 38)), manifest
    assert len(list(preview.glob('page-*.png'))) == 37
    assert len(pdf_pages(preview / 'overview.pdf')) == 5
    print('PASS: external starter, notes, relative assets, all specimens, and multipage previews.',
          flush=True)


if __name__ == '__main__':
    main()
