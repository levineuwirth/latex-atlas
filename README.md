<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 the repository contributors -->

# Atlas

**Beamer presentations with Garamond, engraved diagrams, and room for an argument.**

Atlas is a pair of LuaLaTeX Beamer themes and a small command-line toolkit.
Start with warm paper and restrained typography, or use AtlasGrand for gilded
borders, dark chapter openings, and marginal notes. Ordinary Beamer frames,
mathematics, overlays, and speaker notes remain ordinary LaTeX.

![AtlasGrand: an astronomical opening with an engraved armillary sphere](preview/grand/01-cover.png)

| An argument in motion | A quiet mathematical plate |
|:-:|:-:|
| ![Euler: unfolding a cube into its net](preview/euler/02-net.png) | ![Euler: three solids with the same invariant](preview/euler/08-solids.png) |

## Make your first talk

Clone this repository, or extract a [release bundle](https://github.com/levineuwirth/latex-atlas/releases) and open its directory.
The bundle includes the CLI, themes, starter, sample sources, and ready-to-read
PDFs. Keep that directory intact: the CLI locates its themes and starter there.

```sh
git clone https://github.com/levineuwirth/latex-atlas.git
cd latex-atlas
```

With the dependencies below installed:

```sh
./atlas new ../my-talk
# Edit ../my-talk/talk.tex; put figures in ../my-talk/assets/.
./atlas build ../my-talk/talk.tex
./atlas preview ../my-talk/talk.tex
./atlas check ../my-talk/talk.tex --all-variants
```

The PDF is `../my-talk/build/talk/ornate/talk.pdf`. Preview PNGs and a vector
contact sheet appear in `talk-preview/` beside it. `--plain` selects monochrome;
`--handout` collapses overlays. Each combination has its own build directory.
Run `./atlas --help` or a subcommand's `--help` for options.

The [MIT starter](presentations/starter.tex) provides six copyable patterns:
opening, ordinary content, full figure, enlarged detail, quiet quotation,
and closing. It is one editable `.tex` file, with its example chart included.
Atlas does not automatically turn an essay into a presentation.
The generated `LICENSE-ATLAS` carries the starter's MIT notice without
assigning a license to your own presentation text.

## Install the dependencies

The tested environment is **Ubuntu 24.04**, with Python **3.9 or later**.
The Python tools use only the standard library. Building needs LuaLaTeX and
`latexmk`; previews need Poppler, pdfLaTeX, and `pdfpages`.

```sh
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  python3 latexmk poppler-utils texlive-luatex texlive-latex-extra \
  texlive-fonts-recommended texlive-fonts-extra texlive-plain-generic \
  fonts-texgyre fonts-texgyre-math
luaotfload-tool --update
```

Use the EB Garamond family supplied by TeX Live. Ubuntu's separate
`fonts-ebgaramond` package can select an older family with the same name,
causing font-feature warnings. The theme also needs Garamond-Math and TeX
Gyre Pagella Math; the packages above provide them. On other systems,
install equivalent TeX and Poppler packages; those environments are not
currently covered by CI.

There is no installer or background service. You can run `atlas` by its
absolute path or symlink it onto your `PATH`.

## Explore the presentations

| Presentation | What it demonstrates |
|---|---|
| [Atlas](presentations/atlas.tex) | The base theme, mathematics, blocks, and a speaker-paced tree pursuit |
| [AtlasGrand](presentations/atlas-grand.tex) | The ornate theme: engraved diagrams, chapter openings, and marginal notes |
| [The Form of Two](presentations/atlas-euler.tex) | A complete visual argument through Euler's polyhedral formula |

```sh
./atlas build presentations/atlas-grand.tex --workdir .
./atlas build presentations/atlas-euler.tex --workdir .
```

The release bundle includes the Grand and Euler presentation PDFs, plus a
six-page starter handout. Their slides and sample sources retain the
licenses listed below. The separate [Crawler Chronicles adaptation](docs/presentations.md#crawler-chronicles--the-first-full-essay-adaptation)
remains in the repository with its website terms; it is not in the release
bundle.

## Documentation and checks

- [Presentation guide](docs/presentations.md): CLI options, theme commands,
  overlays, figures, and the full specimen galleries.
- [Release notes and bundle recipe](docs/releases.md): contents, checksums,
  and how to build and test an archive.
- [Earlier experiments](docs/lab.md): the article, print, and verse lab.
- [CI results](https://github.com/levineuwirth/latex-atlas/actions/workflows/ci.yml).

CI tests Python 3.9 and 3.14, audits the diagrams and frozen source assets,
compiles real decks, and checks the extracted release bundle. The `check`
command reports compiler warnings and suspicious text bounds; it cannot
judge every overlap or clipped graphic. Review the generated previews,
and test projection readability in the room where you will present.

## License

The reusable software is **MIT**; authored demonstration material keeps
**ShareAlike**. The Crawler imports retain their website terms, which are
more restrictive than the other demonstrations.

| Material | Terms |
|---|---|
| `sty/`, `tools/`, `atlas`, shell scripts, CI/configuration, and technical documentation | [MIT](LICENSE) |
| `presentations/starter.tex` and `preview/starter/` | [MIT](LICENSE) |
| Reusable `tree-pursuit-helpers.tex`, `grand-plates.tex`, `euler-plates.tex`, `euler-folds.tex`, and `crawler-plates.tex` in `presentations/` | [MIT](LICENSE) |
| Authored Atlas, Grand, and Euler decks; `tree-pursuit.tex` slide text; `examples/`; `bound/`; and their previews | [CC BY-SA 4.0](LICENSE-CONTENT) |
| Crawler essay prose and its authored slide adaptation in `crawler-chronicles.tex` | [CC BY-NC-SA 4.0](presentations/crawler-assets/LICENSE-SOURCE), with source exclusions |
| Crawler graphs, emblems, petition, seal, and derived assets; mixed Crawler previews | Source terms and exclusions in [NOTICES](NOTICES); no additional blanket reuse grant |

You can copy the MIT starter and helpers into your own talk while keeping
their copyright and license notices. Using the tools or theme does not
require your original presentation content to adopt a particular license.
Reusing demonstration text or imported assets is a separate matter: follow
the applicable content license and source notices. MIT components remain
available under MIT when included in a demonstration.

[NOTICES](NOTICES) records attribution and exclusions for imported works,
public-domain poems, quotations, and external dependencies. Frozen Crawler
originals retain their exact bytes; their notices are kept alongside them.
Earlier license grants remain in effect; this change does not rewrite
history or revoke rights already granted.
