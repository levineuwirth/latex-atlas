#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Create, build, preview, and check Atlas talks. Python standard library only."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
NS = '{http://www.w3.org/1999/xhtml}'


class AtlasError(Exception):
    """An actionable command-line error."""


def require(*programs):
    missing = [name for name in programs if not shutil.which(name)]
    if missing:
        raise AtlasError('Missing programs: ' + ', '.join(missing) +
                         '. Install TeX Live (LuaLaTeX/latexmk) and Poppler as needed.')


def tex_path(path):
    # Spaces and Unicode are supported. These characters cannot safely be
    # embedded in our generated TeX filename arguments.
    value = str(path)
    if any(c in value for c in '%{}#\\\n\r"'):
        raise AtlasError(f'Unsupported TeX path characters in {value!r}; rename the path.')
    return r'\detokenize{' + value + '}'


def run_logged(command, cwd, log, env=None):
    with log.open('w') as stream:
        result = subprocess.run(command, cwd=cwd, env=env, stdout=stream,
                                stderr=subprocess.STDOUT)
    if result.returncode:
        tail = '\n'.join(log.read_text(errors='replace').splitlines()[-30:])
        raise AtlasError(f'{command[0]} failed:\n{tail}\nFull output: {log}')


def new_talk(destination):
    destination = destination.expanduser().absolute()
    tex_path(destination)
    # Never merge into an existing directory, including an empty one.
    if destination.exists():
        raise AtlasError(f'Destination already exists: {destination}')
    source = (ROOT / 'presentations/starter.tex').read_text()
    source = source.replace(
        '% In this repo: ./build-beamer.sh --starter [--plain] [--handout]\n'
        '% Elsewhere: TEXINPUTS=/path/to/latex-atlas/sty: lualatex talk.tex (three times).',
        '% Build: atlas build talk.tex [--plain] [--handout]\n'
        '% Review: atlas preview talk.tex; atlas check talk.tex\n'
        '% Put figures in assets/ and reference them as assets/figure.pdf.')
    destination.mkdir(parents=True)
    (destination / 'assets').mkdir()
    (destination / 'assets/.gitkeep').touch()
    (destination / 'talk.tex').write_text(source)
    (destination / '.gitignore').write_text('build/\n')
    # Keep the full MIT notice with a copied template, without licensing
    # the author's new presentation text on their behalf.
    mit = (ROOT / 'LICENSE').read_text().split('MIT License\n', 1)[1]
    (destination / 'LICENSE-ATLAS').write_text(
        'This notice covers the copied Atlas starter code, not your own presentation content.\n\n'
        'MIT License\n' + mit)
    print(f'Created {destination / "talk.tex"}\nEdit the metadata and six marked sections.')


NOTES = ('script', 'presenter')


def build(source, plain=False, handout=False, output_dir=None, workdir=None, force=False,
          notes=None):
    source = source.expanduser().resolve()
    if notes not in (None,) + NOTES:
        raise AtlasError(f'Unknown notes mode {notes!r}; use script or presenter.')
    if notes == 'script' and handout:
        raise AtlasError('--notes script already gives one page per frame; omit --handout.')
    if not source.is_file() or source.suffix.lower() != '.tex':
        raise AtlasError(f'Expected an existing .tex deck: {source}')
    source_arg = tex_path(source)
    require('latexmk', 'lualatex', 'kpsewhich')
    env = os.environ.copy()
    env['TEXINPUTS'] = os.pathsep.join(
        [str(ROOT / 'sty'), str(source.parent), env.get('TEXINPUTS', ''), ''])
    missing = []
    for package in ('beamer.cls', 'fontspec.sty', 'unicode-math.sty', 'tikz.sty',
                    'pgfornament.sty', 'tcolorbox.sty', 'microtype.sty'):
        found = subprocess.run(['kpsewhich', package], env=env, capture_output=True, text=True)
        if not found.stdout.strip():
            missing.append(package)
    if missing:
        raise AtlasError('Missing TeX packages: ' + ', '.join(missing))
    variant = (('plain' if plain else 'ornate') + ('-handout' if handout else '') +
               (f'-{notes}' if notes else ''))
    base = output_dir.expanduser().resolve() if output_dir else source.parent / 'build'
    out = base / source.stem / variant
    tex_path(out)
    cwd = workdir.expanduser().resolve() if workdir else source.parent
    if not cwd.is_dir():
        raise AtlasError(f'Working directory does not exist: {cwd}')
    # A script shows each frame as the audience saw it: its pages come from
    # the handout, which has exactly one page per frame.
    slides = (build(source, plain, True, output_dir, workdir, force)
              if notes == 'script' else None)
    out.mkdir(parents=True, exist_ok=True)
    # A report describes a particular successful check, not a later rebuild.
    (out / 'check.json').unlink(missing_ok=True)
    driver = out / 'atlas-driver.tex'
    content = '% Generated by atlas; edit the source deck.\n'
    if plain:
        content += r'\PassOptionsToPackage{plain}{beamerthemeAtlas,beamerthemeAtlasGrand}' + '\n'
    # A script is read frame by frame, so it collapses overlays as a handout does.
    if handout or notes == 'script':
        content += r'\PassOptionsToClass{handout}{beamer}' + '\n'
    if notes:
        content += r'\def\AtlasNotesMode{' + notes + '}\n'
    if slides:
        content += r'\def\AtlasNotesSlides{' + tex_path(slides) + '}\n'
        content += r'\def\AtlasNotesAux{' + tex_path(slides.with_suffix('.aux')) + '}\n'
    content += r'\input{' + source_arg + '}\n'
    # Keep the timestamp when unchanged, so latexmk can reuse a current build.
    if not driver.exists() or driver.read_text() != content:
        driver.write_text(content)
    command = ['latexmk', '-lualatex', '-interaction=nonstopmode', '-halt-on-error',
               '-file-line-error', '-cd-', '-jobname=talk', f'-outdir={out}']
    if force:
        command.append('-g')
    command.append(str(driver))
    run_logged(command, cwd, out / 'build.stdout.txt', env)
    pdf = out / 'talk.pdf'
    if not pdf.is_file():
        raise AtlasError(f'Build produced no PDF. See {out / "build.stdout.txt"}')
    if slides and log_page_count(pdf) != log_page_count(slides):
        raise AtlasError(f'The script has {log_page_count(pdf)} pages but the handout has '
                         f'{log_page_count(slides)}; each note page must match one frame.')
    print(f'Built {pdf}', flush=True)
    return pdf


def log_page_count(pdf):
    match = re.search(r'Output written on .*?\((\d+) pages?',
                      pdf.with_suffix('.log').read_text(errors='replace'), re.S)
    if not match:
        raise AtlasError(f'Cannot find the page count in {pdf.with_suffix(".log")}')
    return int(match[1])


def pdf_pages(pdf):
    require('pdftotext')
    result = subprocess.run(['pdftotext', '-bbox', str(pdf), '-'], capture_output=True, text=True)
    if result.returncode or result.stderr.strip():
        raise AtlasError(f'Cannot inspect {pdf}: {result.stderr.strip()}')
    # Poppler can map decorative bullets to XML-illegal control characters.
    # Preserve their bounding boxes while removing those characters.
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', result.stdout)
    try:
        pages = ET.fromstring(text).findall(f'.//{NS}page')
    except ET.ParseError as error:
        raise AtlasError(f'Cannot parse PDF text bounds: {error}') from error
    if not pages:
        raise AtlasError(f'No pages found in {pdf}')
    return pages


def select_pages(pages, specification=None, phrases=None):
    selected = []
    if specification:
        for part in specification.split(','):
            match = re.fullmatch(r'\s*(\d+)(?:-(\d+))?\s*', part)
            if not match:
                raise AtlasError('Use page numbers or ascending ranges, for example --pages 1,3-5.')
            first, last = int(match[1]), int(match[2] or match[1])
            if not 1 <= first <= last <= len(pages):
                raise AtlasError(f'Page range {part!r} is outside 1–{len(pages)} or reversed.')
            selected.extend(range(first, last + 1))
    for phrase in phrases or []:
        normalized = ' '.join(phrase.split())
        matches = [i for i, page in enumerate(pages, 1)
                   if normalized in ' '.join(' '.join(page.itertext()).split())]
        if len(matches) != 1 or not normalized:
            raise AtlasError(f'Text selection {phrase!r} matched pages {matches}; '
                             'use a unique phrase or --pages for overlays.')
        selected.extend(matches)
    return list(dict.fromkeys(selected)) if selected else list(range(1, len(pages) + 1))


def preview(pdf, specification=None, phrases=None):
    pdf = pdf.expanduser().resolve()
    if not pdf.is_file():
        raise AtlasError(f'PDF does not exist: {pdf}')
    require('pdftotext', 'pdftoppm', 'pdflatex')
    pages = pdf_pages(pdf)
    selected = select_pages(pages, specification, phrases)
    out = pdf.parent / (pdf.stem + '-preview')
    out.mkdir(exist_ok=True)
    # Stage the input with a fixed name: arbitrary PDF names never enter TeX.
    # Render everything before replacing the last successful preview.
    with tempfile.TemporaryDirectory(prefix='.atlas-preview-', dir=out) as directory:
        stage = Path(directory)
        shutil.copyfile(pdf, stage / 'source.pdf')
        names = []
        for page in selected:
            name = f'page-{page:04d}'
            run_logged(['pdftoppm', '-f', str(page), '-l', str(page), '-scale-to', '1200',
                        '-singlefile', '-png', 'source.pdf', name], stage, stage / 'render.log')
            names.append(name + '.png')
        page_list = ','.join(map(str, selected))
        rows = min(3, (len(selected) + 2) // 3)
        # Up to nine slides per sheet, as many sheets as needed. Preserve live text
        # and vector figures by including the PDF, not the PNG previews.
        tex = ('\\documentclass{article}\n'
               f'\\usepackage[paperwidth=480mm,paperheight={90 * rows}mm,margin=0pt]{{geometry}}\n'
               '\\usepackage{pdfpages}\n\\begin{document}\n'
               f'\\includepdf[pages={{{page_list}}},nup=3x{rows},delta=2mm 2mm,'
               'pagecommand={}]{source.pdf}\n\\end{document}\n')
        (stage / 'overview.tex').write_text(tex)
        run_logged(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'overview.tex'],
                   stage, out / 'preview.stdout.txt')
        manifest = out / 'manifest.json'
        previous = json.loads(manifest.read_text()) if manifest.exists() else {}
        for name in names + ['overview.pdf']:
            shutil.copyfile(stage / name, out / name)
        # Remove only previously recorded, tool-owned page images.
        for name in previous.get('images', []):
            if re.fullmatch(r'page-\d+\.png', name) and name not in names:
                (out / name).unlink(missing_ok=True)
        manifest.write_text(json.dumps({'source': str(pdf), 'pages': selected,
                                        'images': names}, indent=2) + '\n')
    print(f'Previewed {len(selected)} pages: {out / "overview.pdf"}')


def log_findings(text):
    findings = []
    for line in text.splitlines():
        if re.search(r'Overfull \\[hv]box|Underfull \\[hv]box|Missing character:|'
                     r'\bWarning\b|^!|^.*:\d+:', line):
            findings.append(line.strip())
    return list(dict.fromkeys(findings))


def todo_positions(text):
    """Locate draft commands in ordinary TeX, excluding comments and literals.

    This is source lint, not a TeX interpreter: markers in macro definitions
    and conditional branches remain unfinished source. Runtime warnings still
    cover markers generated dynamically or supplied by packages.
    """
    token = re.compile(r'%[^\n]*|\\(?:[A-Za-z@]+|[^\n])')
    literal_env = re.compile(
        r'\s*\{(verbatim\*?|Verbatim|BVerbatim|LVerbatim|lstlisting|minted|comment)\}')
    position = 0
    while match := token.search(text, position):
        command = match[0]
        position = match.end()
        if command in (r'\verb', r'\lstinline'):
            if text[position:position + 1] == '*':
                position += 1
            if command == r'\lstinline' and text[position:position + 1] == '[':
                end = text.find(']', position + 1)
                position = len(text) if end < 0 else end + 1
            if position < len(text) and not text[position].isspace():
                end = text.find(text[position], position + 1)
                position = len(text) if end < 0 else end + 1
        elif command == r'\begin' and (env := literal_env.match(text, position)):
            end = re.search(r'\\end\s*\{' + re.escape(env[1]) + r'\}', text[env.end():])
            position = len(text) if end is None else env.end() + end.end()
        elif command == r'\string':
            while position < len(text) and text[position].isspace():
                position += 1
            following = token.match(text, position)
            position = following.end() if following else position + 1
        elif command == r'\detokenize':
            start = re.match(r'\s*\{', text[position:])
            if start:
                position += start.end()
                depth = 1
                # Escaped braces are control symbols, not argument delimiters.
                delimiters = re.compile(r'%[^\n]*|\\(?:[A-Za-z@]+|[^\n])|[{}]')
                while depth and (part := delimiters.search(text, position)):
                    depth += (part[0] == '{') - (part[0] == '}')
                    position = part.end()
                if depth:
                    position = len(text)
        elif command == r'\AtlasTodo':
            line = text.count('\n', 0, match.start()) + 1
            column = match.start() - text.rfind('\n', 0, match.start())
            yield line, column


def todo_findings(pdf):
    """Use the recorder to lint exactly the .tex files read by this build."""
    recorder = pdf.with_suffix('.fls')
    if not recorder.is_file():
        return []
    lines = recorder.read_text(errors='replace').splitlines()
    cwd = next((Path(line[4:]) for line in lines if line.startswith('PWD ')), pdf.parent)
    seen, findings = set(), []
    for line in lines:
        if not line.startswith('INPUT '):
            continue
        source = (cwd / line[6:]).resolve()
        if source.suffix != '.tex' or source in seen:
            continue
        seen.add(source)
        if source.is_file():
            for number, column in todo_positions(source.read_text(errors='replace')):
                findings.append(f'{source}:{number}:{column}: Unfinished (\\AtlasTodo)')
    return findings


def boundary_findings(pages, margin=1.0):
    findings = []
    for number, page in enumerate(pages, 1):
        width, height = float(page.attrib['width']), float(page.attrib['height'])
        for word in page.iter(NS + 'word'):
            x0, y0, x1, y1 = (float(word.attrib[key]) for key in ('xMin', 'yMin', 'xMax', 'yMax'))
            if x0 < margin or y0 < margin or x1 > width - margin or y1 > height - margin:
                findings.append(f'Page {number}: text within {margin:g} pt of or beyond '
                                f'the page edge: {word.text!r} ({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})')
    return findings


def check(source, args):
    require('pdftotext')
    variants = [(False, False), (False, True), (True, False), (True, True)] if args.all_variants else [(args.plain, args.handout)]
    notes = getattr(args, 'notes', None)
    failed = False
    for plain, handout in variants:
        try:
            pdf = build(source, plain, handout, args.output_dir, args.workdir, force=True,
                        notes=notes)
            pages = pdf_pages(pdf)
            findings = log_findings(pdf.with_suffix('.log').read_text(errors='replace'))
            findings += todo_findings(pdf)
            findings += boundary_findings(pages)
            report = pdf.parent / 'check.json'
            report.write_text(json.dumps({'pdf': str(pdf), 'pages': len(pages),
                                          'findings': findings}, indent=2) + '\n')
            if findings:
                failed = True
                print('\n'.join('  ' + finding for finding in findings))
            print(f'{"REVIEW" if findings else "PASS"}: {len(pages)} pages; '
                  f'{len(findings)} findings. Report: {report}', flush=True)
        except AtlasError as error:
            failed = True
            print(f'FAIL ({"plain" if plain else "ornate"}'
                  f'{", handout" if handout else ""}{", notes " + notes if notes else ""}): '
                  f'{error}', file=sys.stderr)
    print('Page-boundary checks cover extracted text; inspect previews for clipped graphics and overlaps.')
    return 1 if failed else 0


def parser():
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument('--version', action='version',
                         version='Atlas ' + (ROOT / 'VERSION').read_text().strip())
    commands = command.add_subparsers(dest='command', required=True)
    new = commands.add_parser('new', help='Create a talk directory from the six-pattern starter')
    new.add_argument('destination', type=Path, help='A directory that does not yet exist')
    for name, help_text in [('build', 'Compile a deck with LuaLaTeX via latexmk'),
                            ('preview', 'Render a deck or PDF and make a vector contact sheet'),
                            ('check', 'Rebuild, then report log warnings and suspicious text bounds')]:
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument('source', type=Path, help='Deck .tex path' + (' or an existing .pdf' if name == 'preview' else ''))
        sub.add_argument('--plain', action='store_true', help='Use the monochrome Atlas palette')
        sub.add_argument('--handout', action='store_true', help='Collapse overlays using Beamer handout mode')
        sub.add_argument('--notes', choices=NOTES,
                         help='Speaker notes: script (a note page for every frame, notes only) '
                              'or presenter (slide plus notes side by side, e.g. pdfpc --notes=right)')
        sub.add_argument('--output-dir', type=Path, help='Build root (default: build/ beside the deck)')
        sub.add_argument('--workdir', type=Path, help='Resolve relative asset paths here (default: deck directory)')
        if name == 'preview':
            sub.add_argument('--pages', help='One-based PDF pages, e.g. 1,3-5; default: all')
            sub.add_argument('--match', action='append', help='Select a unique text phrase; repeat for more slides')
        if name == 'check':
            sub.add_argument('--all-variants', action='store_true', help='Check ornate/plain × presentation/handout')
    return command


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'new':
            new_talk(args.destination)
        elif args.command == 'check':
            if args.all_variants and (args.plain or args.handout or args.notes):
                raise AtlasError('--all-variants covers --plain and --handout; check --notes separately.')
            return check(args.source, args)
        elif args.command == 'preview' and args.source.suffix.lower() == '.pdf':
            if args.plain or args.handout or args.notes or args.output_dir or args.workdir:
                raise AtlasError('Build options apply to .tex decks, not existing PDFs.')
            preview(args.source, args.pages, args.match)
        else:
            if args.command == 'preview':
                require('pdftotext', 'pdftoppm', 'pdflatex')
            pdf = build(args.source, args.plain, args.handout, args.output_dir, args.workdir,
                        notes=args.notes)
            if args.command == 'preview':
                preview(pdf, args.pages, args.match)
    except (AtlasError, OSError, ValueError) as error:
        print(f'atlas: {error}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('atlas: interrupted', file=sys.stderr)
        return 130
    return 0


if __name__ == '__main__':
    sys.exit(main())
