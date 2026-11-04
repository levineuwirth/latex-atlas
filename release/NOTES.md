<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 the repository contributors -->

# Atlas 0.1.0

The first Atlas release combines two LuaLaTeX Beamer themes with a small
toolkit for writing and reviewing presentations.

- **Atlas:** Garamond text and mathematics, small-cap headings, rubric,
  warm paper, native Beamer blocks, and speaker-paced overlays.
- **AtlasGrand:** gilded borders, engraved diagrams, dark chapter openings,
  marginal notes, and quiet pages for figures and quotations.
- **A six-pattern starter:** opening, content, full figure, detail,
  quotation, and closing, in one editable file.
- **Four commands:** `atlas new`, `build`, `preview`, and `check`, with
  independent monochrome and handout variants.

The bundle includes source and PDF samples of AtlasGrand and *The Form of
Two*, a six-page starter handout, licenses, and a file checksum manifest.
It requires Python 3.9+, LuaLaTeX, latexmk, and Poppler; the README contains
the tested Ubuntu 24.04 installation recipe. There is no Python package
dependency or background service.

Software and reusable templates are MIT. Authored sample narratives are
CC BY-SA 4.0. Crawler material with its separate website terms is omitted
from this release bundle.

This is an initial release. Layout checking covers compiler diagnostics
and extracted text bounds, not every graphical collision. Visual review
and testing in an actual presentation room remain part of preparing a talk.
