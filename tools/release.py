#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Build and test a selected Atlas release bundle; never publish it."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

from atlas_cli import pdf_pages

ROOT = Path(__file__).resolve().parent.parent
# Deliberately enumerate shipped files. Do not recursively copy the checkout:
# the Crawler assets have different reuse terms, and build/ contains local work.
FILES = {
    'README.md': 'release/README.md',
    'CHANGELOG.md': 'release/NOTES.md',
    'NOTICES': 'release/NOTICES',
    'presentations/LICENSE': 'release/PRESENTATIONS-LICENSE',
    'samples/LICENSE': 'release/SAMPLES-LICENSE',
    **{name: name for name in (
        'LICENSE', 'LICENSE-CONTENT', 'VERSION', 'atlas', 'tools/atlas_cli.py',
        'sty/beamerthemeAtlas.sty', 'sty/beamerthemeAtlasGrand.sty',
        'presentations/starter.tex', 'presentations/atlas.tex',
        'presentations/atlas-grand.tex', 'presentations/atlas-euler.tex',
        'presentations/tree-pursuit.tex', 'presentations/tree-pursuit-helpers.tex',
        'presentations/grand-plates.tex', 'presentations/euler-plates.tex',
        'presentations/euler-folds.tex',
    )},
}
SAMPLES = [('atlas-grand', False, 33, 'atlas-grand.pdf'),
           ('atlas-euler', False, 29, 'atlas-euler.pdf'),
           ('starter', True, 6, 'starter-handout.pdf')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_manifest(bundle, version, commit, dirty, compiler):
    return {
        'version': version, 'source_commit': commit, 'source_dirty': dirty,
        'compiler': compiler,
        'files': {str(p.relative_to(bundle)): {'sha256': digest(p), 'bytes': p.stat().st_size}
                  for p in sorted(bundle.rglob('*')) if p.is_file() and p.name != 'MANIFEST.json'},
    }


def write_archive(bundle, target, epoch):
    with target.open('wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=epoch) as zipped:
        with tarfile.open(fileobj=zipped, mode='w', format=tarfile.PAX_FORMAT) as archive:
            for path in sorted(bundle.rglob('*')):
                if not path.is_file():
                    continue
                info = tarfile.TarInfo(bundle.name + '/' + path.relative_to(bundle).as_posix())
                info.size = path.stat().st_size
                info.mtime = epoch
                info.mode = 0o755 if path.relative_to(bundle).as_posix() == 'atlas' else 0o644
                with path.open('rb') as stream:
                    archive.addfile(info, stream)


def unpack_and_verify(archive, destination, folder):
    with tarfile.open(archive, 'r:gz') as packed:
        names = set()
        for member in packed.getmembers():
            path = PurePosixPath(member.name)
            if (not member.isfile() or path.is_absolute() or '..' in path.parts
                    or not path.parts or path.parts[0] != folder or member.name in names):
                raise ValueError(f'Unexpected archive entry: {member.name}')
            names.add(member.name)
            target = destination.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with packed.extractfile(member) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)
            target.chmod(member.mode & 0o777)
    bundle = destination / folder
    manifest = json.loads((bundle / 'MANIFEST.json').read_text())
    actual = {str(p.relative_to(bundle)) for p in bundle.rglob('*') if p.is_file()}
    if actual != set(manifest['files']) | {'MANIFEST.json'}:
        raise ValueError('Archive contents do not match the manifest')
    for name, record in manifest['files'].items():
        path = bundle / name
        if digest(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            raise ValueError(f'Checksum mismatch: {name}')
    return bundle


def run_cli(bundle, arguments, cwd, env):
    print('+ bundled atlas ' + ' '.join(map(str, arguments)), flush=True)
    subprocess.run([str(bundle / 'atlas'), *map(str, arguments)], cwd=cwd, env=env, check=True)


def validate_bundle(archive, folder, output, env):
    with tempfile.TemporaryDirectory(prefix='atlas-release-check-') as temporary:
        outside = Path(temporary) / 'Outside checkout'
        outside.mkdir()
        bundle = unpack_and_verify(archive, outside, folder)
        talk = outside / 'My talk'
        try:
            run_cli(bundle, ['--version'], outside, env)
            run_cli(bundle, ['new', talk], outside, env)
            if 'Permission is hereby granted' not in (talk / 'LICENSE-ATLAS').read_text():
                raise ValueError('The generated talk is missing the starter MIT notice')
            run_cli(bundle, ['check', talk / 'talk.tex', '--all-variants'], outside, env)
            counts = {}
            for variant, expected in [('ornate', 7), ('ornate-handout', 6),
                                      ('plain', 7), ('plain-handout', 6)]:
                built = talk / 'build/talk' / variant
                report = json.loads((built / 'check.json').read_text())
                if report['findings'] or report['pages'] != expected:
                    raise ValueError(f'Unexpected extracted starter result: {report}')
                recorded = (built / 'talk.fls').read_text()
                if str(ROOT) in recorded or str(bundle / 'sty/beamerthemeAtlasGrand.sty') not in recorded:
                    raise ValueError('Extracted build did not use only the bundled Atlas themes')
                counts[variant] = expected
            run_cli(bundle, ['preview', talk / 'build/talk/ornate/talk.pdf', '--pages', '1,3-7'], outside, env)
            preview = talk / 'build/talk/ornate/talk-preview'
            if len(pdf_pages(preview / 'overview.pdf')) != 1 or len(list(preview.glob('page-*.png'))) != 6:
                raise ValueError('Extracted preview has unexpected page/image counts')
            return {'status': 'passed', 'archive_sha256': digest(archive),
                    'starter_pages': counts, 'preview_slides': 6,
                    'themes_loaded_from_extracted_bundle': True}
        finally:
            # Keep diagnostics even if the temporary extraction fails a check.
            if (talk / 'build').exists():
                shutil.copytree(talk / 'build', output / 'verification', dirs_exist_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build/release')
    parser.add_argument('--allow-dirty', action='store_true', help='Development only; record uncommitted sources')
    args = parser.parse_args(argv)
    version = (ROOT / 'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?', version):
        parser.error('VERSION must be a release version such as 0.1.0 or 0.1.0-rc.1')
    git = lambda *items: subprocess.check_output(['git', *items], cwd=ROOT, text=True).strip()
    commit = git('rev-parse', 'HEAD')
    dirty = bool(git('status', '--porcelain'))
    if dirty and not args.allow_dirty:
        parser.error('Commit the working tree first, or use --allow-dirty for local development')
    epoch = int(git('show', '-s', '--format=%ct', 'HEAD'))
    output = args.output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / 'release-check.json').unlink(missing_ok=True)
    env = os.environ.copy()
    env.update(TEXINPUTS='', PYTHONPATH='', SOURCE_DATE_EPOCH=str(epoch), FORCE_SOURCE_DATE='1')
    compiler = subprocess.check_output(['lualatex', '--version'], text=True).splitlines()[0]
    folder = 'latex-atlas-' + version
    archive = output / (folder + '.tar.gz')
    with tempfile.TemporaryDirectory(prefix='atlas-release-build-') as temporary:
        bundle = Path(temporary) / folder
        for target, source in FILES.items():
            destination = bundle / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source, destination)
        (bundle / 'atlas').chmod(0o755)
        for stem, handout, expected, filename in SAMPLES:
            arguments = ['check', bundle / 'presentations' / (stem + '.tex'),
                         '--workdir', bundle, '--output-dir', output / 'work']
            if handout:
                arguments.append('--handout')
            run_cli(bundle, arguments, bundle, env)
            built = output / 'work' / stem / ('ornate-handout' if handout else 'ornate')
            report = json.loads((built / 'check.json').read_text())
            if report['findings'] or report['pages'] != expected:
                raise ValueError(f'Unexpected sample result: {report}')
            shutil.copyfile(built / 'talk.pdf', bundle / 'samples' / filename)
            shutil.copyfile(built / 'talk.pdf', output / filename)
        manifest = make_manifest(bundle, version, commit, dirty, compiler)
        (bundle / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
        write_archive(bundle, archive, epoch)
    validation = validate_bundle(archive, folder, output, env)
    validation.update(source_commit=commit, source_dirty=dirty, version=version)
    (output / 'release-check.json').write_text(json.dumps(validation, indent=2) + '\n')
    assets = [archive, *(output / name for _, _, _, name in SAMPLES)]
    (output / 'SHA256SUMS').write_text(''.join(f'{digest(path)}  {path.name}\n' for path in assets))
    print(f'PASS: verified release bundle {archive} ({archive.stat().st_size:,} bytes)', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'release: {error}', file=sys.stderr)
        sys.exit(1)
