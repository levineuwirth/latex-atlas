# latex-atlas

A LaTeX styling lab. Each file in `examples/` is a standalone plate that
puts a few typographic devices on one page, in the register of the early
presses, the engraver's shop, or the *Principia*. Some of the devices are
functional and might graduate into a preprint style; some are pure
costume and are here because they are a pleasure to build. The lab does
not choose between them. It shows what each one contributes.

Companion to `vintage-latex` (`/home/jeans/scratch/tmp/vintage-latex`),
the gallery of period pastiches; kept separate so this repo can grow
toward reusable website preprint styles.

## Gallery

| | | |
|:-:|:-:|:-:|
| [![01](preview/01-rubricated-incipit.png)](examples/01-rubricated-incipit.tex) | [![02](preview/02-marginal-scholia.png)](examples/02-marginal-scholia.tex) | [![03](preview/03-hatched-bar-chart.png)](examples/03-hatched-bar-chart.tex) |
| 01 rubricated incipit | 02 marginal scholia | 03 hatched bar chart |
| [![04](preview/04-propositions.png)](examples/04-propositions.tex) | [![05](preview/05-engraved-graph-plate.png)](examples/05-engraved-graph-plate.tex) | [![06](preview/06-hand-press-impression.png)](examples/06-hand-press-impression.tex) |
| 04 propositions | 05 engraved graph plate | 06 hand-press impression |

## Examples

| no | file | what it isolates | controls |
|----|------|------------------|----------|
| 01 | `01-rubricated-incipit.tex` | two-colour rubrication: the colour, and each device that carries it | paper, rubric, pilcrow, initial, runhead |
| 02 | `02-marginal-scholia.tex` | the gloss in the margin against the footnote, and the page cut to make room for it | paper, margin, gloss, catchword, folio |
| 03 | `03-hatched-bar-chart.tex` | series by hatch against grey fill; the table of the record; lining figures | paper, hatch, table, lining |
| 04 | `04-propositions.tex` | theorem apparatus after the *Principia* against amsthm; a math font cut for the text against Latin Modern | mathfont, paper, heads, qed, scholium |
| 05 | `05-engraved-graph-plate.tex` | an engraved plate of two graphs: tapered burin strokes, hatched spheres, a matching by line weight, frame and lettering | paper, taper, matching, stipple, frame, lettering |
| 06 | `06-hand-press-impression.tex` | the hand press, counterfeited in a LuaTeX callback: baseline scatter, ink squash, uneven inking, laid paper, foxing | paper, jitter, inkspread, inking, laid, foxing |

Every control has a *modern default*: what you get from the document
class, the plotting library, or the engine when you do nothing. The
ablation of a marginal gloss is a footnote, of a hatch a grey ramp, of
Q.E.D. a tombstone, of parchment white paper. So each lab variant is a
fair comparison, not a page with a hole in it.

`paper` is a control in every plate. The tints differ slightly per plate
(`F5EDDC`, `F4EBDD`, `F4EAD8`, `F5ECDB`, `F6EFE1`, `F3E9D6`): deliberate
per-plate tuning, not a shared token yet. Ablating it across all six is
how that question gets decided.

## Build

```sh
./build.sh                          # every plate, full treatment, into build/
./build.sh 04-propositions          # a subset
./build.sh --ablate                 # also every lab variant, into build/ablate/
./preview.sh                        # PNGs into preview/ and preview/ablate/
./gallery.sh                        # regenerate the lab gallery in this README
```

Requirements: LuaLaTeX (TeX Live 2026), `fontspec`, `unicode-math`,
`amsthm`, `geometry`, `microtype`, `xcolor`, `tikz` (+ `calc`,
`patterns.meta`), `pgfornament`, `fancyhdr`, `lettrine`, `luacode`.
EB Garamond and Garamond-Math if present (`texlive-fontsextra`), else
TeX Gyre Pagella and Pagella Math; the committed previews are the
Garamond renderings. Previews need poppler's `pdftoppm`; they are
byte-reproducible from a clean build, so a rebuild leaves the tree clean.

## The lab

Each plate carries this block after `\documentclass`, identical in every
file so that the files stay standalone:

```latex
\atlascontrol{<name>}{<treatment>}{<modern default>}
```

The treatment is set unless `<name>` appears in `\atlasomit`, a comma
list that `build.sh --ablate` passes on the `lualatex` command line, so no
file is edited to produce a variant. For each plate the lab compiles one
variant per control with that control at its modern default, and one
`--plain` variant with all of them. `\atlasstamp`, at the foot of every
plate, prints the controls and which of them the impression has set to
the default, so each PNG below names itself.

To add a plate: copy the lab block, wrap each device you want to test in
`\atlascontrol` with an honest modern default in the third argument, end
the plate with `\atlasstamp`, and run the three scripts. `build.sh` finds
the controls by grepping for `\atlascontrol{name}`, so a name is
lower-case letters, digits and hyphens.

<!-- lab:begin -->

### 01 rubricated incipit

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/01-rubricated-incipit.png)](examples/01-rubricated-incipit.tex) | ![without paper](preview/ablate/01-rubricated-incipit--no-paper.png) | ![without rubric](preview/ablate/01-rubricated-incipit--no-rubric.png) | ![without pilcrow](preview/ablate/01-rubricated-incipit--no-pilcrow.png) |
| full | without paper | without rubric | without pilcrow |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without initial](preview/ablate/01-rubricated-incipit--no-initial.png) | ![without runhead](preview/ablate/01-rubricated-incipit--no-runhead.png) | ![plain](preview/ablate/01-rubricated-incipit--plain.png) | |
| without initial | without runhead | plain | |

### 02 marginal scholia

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/02-marginal-scholia.png)](examples/02-marginal-scholia.tex) | ![without paper](preview/ablate/02-marginal-scholia--no-paper.png) | ![without margin](preview/ablate/02-marginal-scholia--no-margin.png) | ![without gloss](preview/ablate/02-marginal-scholia--no-gloss.png) |
| full | without paper | without margin | without gloss |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without catchword](preview/ablate/02-marginal-scholia--no-catchword.png) | ![without folio](preview/ablate/02-marginal-scholia--no-folio.png) | ![plain](preview/ablate/02-marginal-scholia--plain.png) | |
| without catchword | without folio | plain | |

### 03 hatched bar chart

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/03-hatched-bar-chart.png)](examples/03-hatched-bar-chart.tex) | ![without paper](preview/ablate/03-hatched-bar-chart--no-paper.png) | ![without hatch](preview/ablate/03-hatched-bar-chart--no-hatch.png) | ![without table](preview/ablate/03-hatched-bar-chart--no-table.png) |
| full | without paper | without hatch | without table |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without lining](preview/ablate/03-hatched-bar-chart--no-lining.png) | ![plain](preview/ablate/03-hatched-bar-chart--plain.png) | | |
| without lining | plain | | |

### 04 propositions

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/04-propositions.png)](examples/04-propositions.tex) | ![without mathfont](preview/ablate/04-propositions--no-mathfont.png) | ![without paper](preview/ablate/04-propositions--no-paper.png) | ![without heads](preview/ablate/04-propositions--no-heads.png) |
| full | without mathfont | without paper | without heads |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without qed](preview/ablate/04-propositions--no-qed.png) | ![without scholium](preview/ablate/04-propositions--no-scholium.png) | ![plain](preview/ablate/04-propositions--plain.png) | |
| without qed | without scholium | plain | |

### 05 engraved graph plate

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/05-engraved-graph-plate.png)](examples/05-engraved-graph-plate.tex) | ![without paper](preview/ablate/05-engraved-graph-plate--no-paper.png) | ![without taper](preview/ablate/05-engraved-graph-plate--no-taper.png) | ![without matching](preview/ablate/05-engraved-graph-plate--no-matching.png) |
| full | without paper | without taper | without matching |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without stipple](preview/ablate/05-engraved-graph-plate--no-stipple.png) | ![without frame](preview/ablate/05-engraved-graph-plate--no-frame.png) | ![without lettering](preview/ablate/05-engraved-graph-plate--no-lettering.png) | ![plain](preview/ablate/05-engraved-graph-plate--plain.png) |
| without stipple | without frame | without lettering | plain |

### 06 hand press impression

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/06-hand-press-impression.png)](examples/06-hand-press-impression.tex) | ![without paper](preview/ablate/06-hand-press-impression--no-paper.png) | ![without jitter](preview/ablate/06-hand-press-impression--no-jitter.png) | ![without inkspread](preview/ablate/06-hand-press-impression--no-inkspread.png) |
| full | without paper | without jitter | without inkspread |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without inking](preview/ablate/06-hand-press-impression--no-inking.png) | ![without laid](preview/ablate/06-hand-press-impression--no-laid.png) | ![without foxing](preview/ablate/06-hand-press-impression--no-foxing.png) | ![plain](preview/ablate/06-hand-press-impression--plain.png) |
| without inking | without laid | without foxing | plain |

<!-- lab:end -->

## Toward website preprints

Kept as a standalone lab for now. When a treatment proves itself here,
it graduates to a shared `.sty` for preprints exported to
`levineuwirth.org` (sources live in `~/Repos/research/meyniel`, export
via `make export`). What the lab suggests so far: the gloss, the
apparatus of 04, and the monochrome discipline of 03 and 05 are
candidates; the frame, the lettering and everything in 06 are costume,
and stay here. No vault (`~/universum`) material enters this repo.

## License

CC BY-SA 4.0, see `LICENSE`. Third-party deps (e.g. `fiziko` if later
examples use it) are not relicensed here.
