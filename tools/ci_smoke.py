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

from atlas_cli import pdf_pages

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

    # A long deck must make multiple overview sheets, preserving every page.
    crawler = OUT / 'specimens/crawler-chronicles/ornate/talk.pdf'
    cli('preview', crawler)
    preview = crawler.parent / 'talk-preview'
    manifest = json.loads((preview / 'manifest.json').read_text())
    assert manifest['pages'] == list(range(1, 38)), manifest
    assert len(list(preview.glob('page-*.png'))) == 37
    assert len(pdf_pages(preview / 'overview.pdf')) == 5
    print('PASS: external starter, relative assets, all specimens, and multipage previews.', flush=True)


if __name__ == '__main__':
    main()
