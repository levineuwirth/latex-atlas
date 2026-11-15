<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 the repository contributors -->

# Atlas 0.2.0

Atlas 0.2.0 prepares a talk for the room: speaker notes, a set of slide
patterns proven in real talks, and checks that an unfinished deck cannot pass.

- **Speaker notes.** Write ordinary `\note{...}`; build with
  `--notes script` or `--notes presenter` (with `build`, `preview`, or
  `check`). A script has one page per frame, with frames lacking notes
  marked, the audience's folio, the frame title, and a picture of the slide
  as shown. A presenter build puts the slide beside its notes for a console
  such as `pdfpc --notes=right`. Notes shrink through four sizes to fit; a
  note too long for its page fails `check` and names the slide.
- **The AtlasGrand slide kit.** `\AtlasGrandQuiet` and `\AtlasGrandWhite`
  pages; `\AtlasGrandStatement`, `\AtlasGrandStat`, and `\AtlasGrandAside`
  for text; `\AtlasGrandExhibit` for a full-page figure or photograph with
  label and caption; and `\AtlasGrandPhoto`, a gilt-framed photograph that
  scales without distortion and leaves a labelled slot until the file exists.
- **Draft markers.** `\AtlasTodo{...}` (both themes) marks an unfinished
  passage on the slide. `check` reports each remaining marker by file, line,
  and column, and each missing photograph, so a draft cannot pass.
- **Recoloured emblems.** `\AtlasEmblem` selects an emblem's palette
  version and its monochrome version under `--plain`.

The starter now uses the kit in place of its own page helpers. Existing
decks render unchanged; the bundled samples are pixel-identical to 0.1.0.
`--notes script` cannot be combined with `--handout` (a script already has
one page per frame), and `check --all-variants` does not include notes.

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
