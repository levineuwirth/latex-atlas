#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Freeze the author's essay assets, preserving the four original graphs.

Run explicitly to refresh from the website. Normal deck builds only read
the committed PDFs. Detail crops alter the viewport, never plot contents.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.home()/
        'Repos/personal/levineuwirth.org/content/essays/crawler_chronicles')
    args = parser.parse_args()
    out = Path(__file__).resolve().parent.parent/'presentations/crawler-assets'
    originals = out/'originals'
    originals.mkdir(parents=True, exist_ok=True)
    selected = {
        'essay.md': 'index.md',
        'repository-targets.svg': 'figures/repository-targets.svg',
        'publication-timeline.svg': 'figures/publication-timeline.svg',
        'episode-contributions.svg': 'data/commit-response/results/figures/episode-contributions.svg',
        'request-vs-publication.svg': 'data/commit-response/results/figures/request-vs-publication.svg',
        'mark.svg': 'mark.svg',
        'petition.pdf': 'exhibits/court-of-unnecessary-computation/notice.pdf',
        'court-seal.pdf': 'exhibits/court-of-unnecessary-computation/court-seal.pdf',
        'repository-targets-metadata.json': 'data/repository-targets-metadata.json',
        'publication-timeline-summary.json': 'data/publication-timeline-summary.json',
    }
    manifest = {'source': str(args.source), 'files': {}, 'derived': {}}
    for name, relative in selected.items():
        data = (args.source/relative).read_bytes()
        (originals/name).write_bytes(data)
        manifest['files'][name] = {'source': relative, 'sha256': hashlib.sha256(data).hexdigest()}
    for name in ['repository-targets','publication-timeline','episode-contributions','request-vs-publication']:
        subprocess.run(['rsvg-convert','-f','pdf','-o',str(out/f'{name}.pdf'),
                        str(originals/f'{name}.svg')], check=True)
    for name in ['petition','court-seal']:
        shutil.copyfile(originals/f'{name}.pdf',out/f'{name}.pdf')
    # Normalize the cover's PDF resource dictionary for LuaTeX inclusion.
    # Cairo keeps vector artwork and text; the complete source is untouched.
    subprocess.run(['pdftocairo','-pdf','-f','1','-l','1',
                    str(originals/'petition.pdf'),str(out/'petition-cover.pdf')],check=True)
    manifest['derived']['petition-cover']={'source':'petition.pdf','page':1,
        'operation':'vector PDF re-emission by pdftocairo for inclusion'}

    # Crop bounds use the original SVG coordinate system (points).
    for name, source, bounds in [
        ('episode-null','episode-contributions',(520,0,275.209988,328.121787)),
        ('request-primary','request-vs-publication',(0,29,302,333.70825)),
    ]:
        root = ET.parse(originals/f'{source}.svg').getroot()
        selected_axis = 'axes_2' if name=='episode-null' else 'axes_1'
        assert sum(e.get('id')==selected_axis for e in root.iter())==1, source
        # Neighbouring panel titles can overhang the selected viewport.
        # Remove only those other panels; keep the selected axes untouched.
        for parent in root.iter():
            for child in list(parent):
                identifier = child.get('id','')
                if identifier.startswith('axes_') and identifier != selected_axis:
                    parent.remove(child)
        x,y,w,h = bounds
        root.set('viewBox', f'{x} {y} {w} {h}')
        root.set('width', f'{w}pt'); root.set('height', f'{h}pt')
        target = out/f'{name}.svg'
        ET.ElementTree(root).write(target, encoding='utf-8',xml_declaration=True)
        subprocess.run(['rsvg-convert','-f','pdf','-o',str(out/f'{name}.pdf'),str(target)],check=True)
        manifest['derived'][name] = {'source': f'{source}.svg','viewport': bounds,'axes_group':selected_axis}

    essay = (originals/'essay.md').read_text()
    main_text = essay.split('::: {.aftermatter')[0]
    svgs = re.findall(r'<svg\b.*?</svg>',main_text,re.S)
    assert len(svgs)==2, 'Expected the original spider and Anubis roundels.'
    # Only currentColor is substituted, for use on the existing palettes.
    for name, svg in [('spider',(originals/'mark.svg').read_text()),('scales',svgs[1])]:
        for palette,color in [('gold','#D9B879'),('ink','#29221B'),('plain','#000000')]:
            root = ET.fromstring(svg.replace('currentColor',color))
            root.set('width','280');root.set('height','280')
            target=out/f'{name}-{palette}.svg'
            ET.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
            subprocess.run(['rsvg-convert','-f','pdf','-o',str(target.with_suffix('.pdf')),str(target)],check=True)
            manifest['derived'][f'{name}-{palette}']={'source':'mark.svg' if name=='spider' else 'essay.md inline scales','color':color}
    manifest['converter']=subprocess.check_output(['rsvg-convert','--version'],text=True).strip()
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Frozen four original graphs, two detail crops, the petition, seal, and original emblems.')


if __name__=='__main__':
    main()
