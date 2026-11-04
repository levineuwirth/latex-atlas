#!/usr/bin/env python3
"""Render the grand specimen's gallery and a single-page PDF contact sheet.

Run after ./build-beamer.sh --grand. Pages are located by their text so that
inserting a frame does not silently make the gallery show the wrong plate.
Requires Poppler (pdftotext/pdftoppm) and pdfLaTeX for PDF imposition only.
"""

from pathlib import Path
import re
import subprocess


def render_gallery(job, gallery, selections):
    """Select unique text, or an explicitly counted overlay occurrence.

    Each selection is (name, phrase) or (name, phrase, expected_count, index).
    The index is one-based; the expected count guards against stale overlays.
    """
    root = Path(__file__).resolve().parent.parent
    build = root / "build" / "beamer"
    pdf = build / f"{job}.pdf"
    if not pdf.exists():
        raise SystemExit(f"Build the specimen first: {pdf.name} is missing.")
    text = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    pages = [re.sub(r"\s+", " ", page).strip() for page in text.split("\f")]
    selected = []
    for name, phrase, *overlay in selections:
        matches = [i + 1 for i, page in enumerate(pages) if phrase in page]
        if not matches:
            raise SystemExit(f"No page contains {phrase!r}; update the gallery selection.")
        expected, index = overlay or (1, 1)
        if len(matches) != expected or not 1 <= index <= expected:
            raise SystemExit(f"Ambiguous gallery selection {phrase!r}: pages {matches}.")
        selected.append((name, matches[index-1]))

    out = root / "preview" / gallery
    out.mkdir(parents=True, exist_ok=True)
    for name, page in selected:
        subprocess.run([
            "pdftoppm", "-f", str(page), "-l", str(page), "-scale-to", "1200",
            "-singlefile", "-png", str(pdf), str(out / name),
        ], check=True)

    # Preserve vector paths and live text in the overview, rather than
    # making a composite raster image of the preview PNGs.
    page_list = ",".join(str(page) for _, page in selected)
    rows = (len(selected) + 2) // 3
    tex = build / f"{job}-overview.tex"
    tex.write_text(
        r"\documentclass{article}" "\n"
        rf"\usepackage[paperwidth=480mm,paperheight={90*rows}mm,margin=0pt]{{geometry}}" "\n"
        r"\usepackage{pdfpages}" "\n"
        r"\begin{document}" "\n"
        rf"\includepdf[pages={{{page_list}}},nup=3x{rows},delta=2mm 2mm,"
        rf"pagecommand={{}}]{{build/beamer/{job}.pdf}}" "\n"
        r"\end{document}" "\n"
    )
    with (build / f"{job}-overview.stdout.txt").open("w") as log:
        subprocess.run([
            "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
            "-output-directory=build/beamer", str(tex),
        ], cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
    print(f"Rendered preview/{gallery}/ and build/beamer/{job}-overview.pdf")
    print("Selected PDF pages:", page_list)


def main():
    render_gallery("atlas-grand", "grand", [
        ("01-cover", "De venatione in arboribus"),
        ("02-chapter", "Liber I The field"),
        ("03-proposition", "Propositio I"),
        ("04-chase", "IV. The narrowing"),
        ("05-proof", "III. Finiteness"),
        ("06-chart", "The account of territory"),
        ("07-two-boundaries", "The next advance captures the robber."),
        ("08-marginalia", "A leaf for the marginal reader"),
        ("09-finis", "Finis"),
    ])


if __name__ == "__main__":
    main()
