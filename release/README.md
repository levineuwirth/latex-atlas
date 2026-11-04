<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 the repository contributors -->
<!-- This file becomes README.md at the root of the release bundle. -->

# Atlas 0.1.0

Beamer presentations with Garamond, engraved diagrams, and room for an argument.

This bundle contains the Atlas and AtlasGrand themes, the `atlas` CLI, a
six-pattern starter, and sample presentation sources and PDFs. Keep this
directory intact: the CLI finds its themes and starter relative to itself.
No Git checkout or access to the original repository is needed to use it.

## Dependencies

Python 3.9+, LuaLaTeX, latexmk, and Poppler are required. The Python tool
uses only the standard library. Contact sheets also use pdfLaTeX and pdfpages.
The tested installation on Ubuntu 24.04 is:

```sh
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  python3 latexmk poppler-utils texlive-luatex texlive-latex-extra \
  texlive-fonts-recommended texlive-fonts-extra texlive-plain-generic \
  fonts-texgyre fonts-texgyre-math
luaotfload-tool --update
```

Use TeX Live's EB Garamond family. Ubuntu's separate `fonts-ebgaramond`
package can shadow it with an older family and cause font-feature warnings.
Other operating systems need equivalent dependencies and are not covered
by the current CI. Font binaries and TeX itself are not bundled.

## Your first talk

From this extracted directory:

```sh
./atlas new ../my-talk
# Edit ../my-talk/talk.tex; add your figures to ../my-talk/assets/.
./atlas build ../my-talk/talk.tex
./atlas preview ../my-talk/talk.tex
./atlas check ../my-talk/talk.tex --all-variants
```

The PDF is `../my-talk/build/talk/ornate/talk.pdf`; its preview directory is
`talk-preview/` beside it. Add `--plain` for monochrome, or `--handout` to
collapse overlays. Run `./atlas --help` and `./atlas --version` for help and
the version. You can also invoke this `atlas` by absolute path or symlink
it onto `PATH` while keeping the bundle directory intact.
The new talk's `LICENSE-ATLAS` preserves the starter's MIT notice; it does
not assign a license to your own presentation text.

`check` reports compilation warnings and suspicious text bounds. Review
the previews for visual collisions and clipped graphics too.

## Read the samples

- [AtlasGrand](samples/atlas-grand.pdf): the ornate theme and engraved diagrams.
- [The Form of Two](samples/atlas-euler.pdf): a visual proof of Euler's formula.
- [Starter handout](samples/starter-handout.pdf): six layouts to copy and edit.

The PDF presentations include speaker-paced overlays; advance pages to
reveal the next step. Their `.tex` sources are in `presentations/`.

```sh
./atlas build presentations/atlas-grand.tex --workdir .
./atlas build presentations/atlas-euler.tex --workdir .
```

## Licenses and provenance

The CLI, themes, starter, reusable helpers, and this documentation are
[MIT](LICENSE). The authored Grand/Euler/Atlas sample narratives and their
PDFs are [CC BY-SA 4.0](LICENSE-CONTENT). See [NOTICES](NOTICES),
[presentation notices](presentations/LICENSE), and [sample notices](samples/LICENSE).
Your own original talk content does not have to adopt those licenses merely
because you use the MIT tools or template.

`MANIFEST.json` records the source commit and SHA-256 of every other bundled
file. `SHA256SUMS`, distributed beside the archive, verifies the archive and
the separately downloadable sample PDFs. The release omits the Crawler
material and the earlier article/verse experiments.

[Release notes](CHANGELOG.md) · [Repository](https://github.com/levineuwirth/latex-atlas)
