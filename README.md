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
| [![07](preview/07-front-matter.png)](examples/07-front-matter.tex) | [![08](preview/08-bibliography.png)](examples/08-bibliography.tex) | [![09](preview/09-verse-page.png)](examples/09-verse-page.tex) |
| 07 front matter | 08 bibliography | 09 verse page |

## Examples

| no | file | what it isolates | controls |
|----|------|------------------|----------|
| 01 | `01-rubricated-incipit.tex` | two-colour rubrication: the colour, and each device that carries it | paper, rubric, pilcrow, initial, runhead |
| 02 | `02-marginal-scholia.tex` | the gloss in the margin against the footnote, and the page cut to make room for it | paper, margin, gloss, catchword, folio |
| 03 | `03-hatched-bar-chart.tex` | series by hatch against grey fill; the table of the record; lining figures | paper, hatch, table, lining |
| 04 | `04-propositions.tex` | theorem apparatus after the *Principia* against amsthm; a math font cut for the text against Latin Modern | mathfont, paper, heads, qed, scholium |
| 05 | `05-engraved-graph-plate.tex` | an engraved plate of two graphs: tapered burin strokes, hatched spheres, a matching by line weight, frame and lettering | paper, taper, matching, stipple, frame, lettering |
| 06 | `06-hand-press-impression.tex` | the hand press, counterfeited in a LuaTeX callback: baseline scatter, ink squash, uneven inking, laid paper, foxing | paper, jitter, inkspread, inking, laid, foxing |
| 07 | `07-front-matter.tex` | the leaf before 04: a period title block against `\maketitle`, *The Argument* against the abstract, a Table of the Propositions with their statements against a list of theorems, fleurons, the imprint against the date; the period's ct/st ties against the common ligatures | ligatures, paper, imprint, title, argument, table, fleuron |
| 08 | `08-bibliography.tex` | the last leaf of 04 and 07: the authorities cited by name and year and listed under the name, by a real `.bbx`/`.cbx` written in the plate, against biblatex's numeric default; small-capital family names, old-style figures for the whole leaf, the DOI as text without the URL | oldstyle, paper, names, smallcaps, doi |
| 09 | `09-verse-page.tex` | a page of verse as a book of poems sets one: the block centred on its longest line against the class's indented `verse`, a two-line initial, the title in small capitals, every fifth line numbered, the source set right, a tailpiece; Herbert's *Vertue* (1633) | paper, rubric, numbers, block, title, initial, attribution, tailpiece |

Every control has a *modern default*: what you get from the document
class, the plotting library, or the engine when you do nothing. The
ablation of a marginal gloss is a footnote, of a hatch a grey ramp, of
Q.E.D. a tombstone, of parchment white paper. So each lab variant is a
fair comparison, not a page with a hole in it.

`paper` is a control in every plate. The tints differ slightly per plate
(`F5EDDC`, `F4EBDD`, `F4EAD8`, `F5ECDB`, `F6EFE1`, `F3E9D6`; 07 and 08
take 04's, being the same book): deliberate per-plate tuning, not a
shared token yet. Ablating it across all eight is how that question gets
decided.

## Build

```sh
./build.sh                          # every plate, full treatment, into build/
./build.sh 04-propositions          # a subset
./build.sh --ablate                 # also every lab variant, into build/ablate/
./build.sh -j --ablate              # the same, one job per core (-j4 for four)
./preview.sh                        # PNGs into preview/ and preview/ablate/
./gallery.sh                        # regenerate the lab gallery in this README
```

One `lualatex` run per PDF is the rule. A plate that needs more declares
it in its header, next to `%!TEX program`, and every variant inherits the
declaration:

```latex
%!ATLAS passes=3
%!ATLAS biber
```

`passes=N` runs `lualatex` N times under the same jobname; `biber` runs
biber after the first pass, on the `.bcf` in the output directory. 08 is
the plate that needs both.

Requirements: LuaLaTeX (TeX Live 2026), `fontspec`, `unicode-math`,
`amsthm`, `geometry`, `microtype`, `xcolor`, `tikz` (+ `calc`,
`patterns.meta`), `pgfornament`, `fancyhdr`, `lettrine`, `needspace`, `luacode`,
`biblatex` with `biber`.
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
lower-case letters, digits and hyphens. A plate must stay one file: what
it needs beyond the TeX distribution it writes itself, as 08 writes its
`.bib`, `.bbx` and `.cbx` in `filecontents*` blocks under `\jobname`.

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

### 07 front matter

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/07-front-matter.png)](examples/07-front-matter.tex) | ![without ligatures](preview/ablate/07-front-matter--no-ligatures.png) | ![without paper](preview/ablate/07-front-matter--no-paper.png) | ![without imprint](preview/ablate/07-front-matter--no-imprint.png) |
| full | without ligatures | without paper | without imprint |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without title](preview/ablate/07-front-matter--no-title.png) | ![without argument](preview/ablate/07-front-matter--no-argument.png) | ![without table](preview/ablate/07-front-matter--no-table.png) | ![without fleuron](preview/ablate/07-front-matter--no-fleuron.png) |
| without title | without argument | without table | without fleuron |

| | | | |
|:-:|:-:|:-:|:-:|
| ![plain](preview/ablate/07-front-matter--plain.png) | | | |
| plain | | | |

### 08 bibliography

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/08-bibliography.png)](examples/08-bibliography.tex) | ![without oldstyle](preview/ablate/08-bibliography--no-oldstyle.png) | ![without paper](preview/ablate/08-bibliography--no-paper.png) | ![without names](preview/ablate/08-bibliography--no-names.png) |
| full | without oldstyle | without paper | without names |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without smallcaps](preview/ablate/08-bibliography--no-smallcaps.png) | ![without doi](preview/ablate/08-bibliography--no-doi.png) | ![plain](preview/ablate/08-bibliography--plain.png) | |
| without smallcaps | without doi | plain | |

### 09 verse page

| | | | |
|:-:|:-:|:-:|:-:|
| [![full](preview/09-verse-page.png)](examples/09-verse-page.tex) | ![without paper](preview/ablate/09-verse-page--no-paper.png) | ![without rubric](preview/ablate/09-verse-page--no-rubric.png) | ![without numbers](preview/ablate/09-verse-page--no-numbers.png) |
| full | without paper | without rubric | without numbers |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without block](preview/ablate/09-verse-page--no-block.png) | ![without title](preview/ablate/09-verse-page--no-title.png) | ![without initial](preview/ablate/09-verse-page--no-initial.png) | ![without attribution](preview/ablate/09-verse-page--no-attribution.png) |
| without block | without title | without initial | without attribution |

| | | | |
|:-:|:-:|:-:|:-:|
| ![without tailpiece](preview/ablate/09-verse-page--no-tailpiece.png) | ![plain](preview/ablate/09-verse-page--plain.png) | | |
| without tailpiece | plain | | |

<!-- lab:end -->

## The style

`sty/atlas.sty` is the graduation: the treatments plates 04, 07 and 08
share, plus what a whole document needs and a single plate never shows
(a title leaf printed once, running heads, folios). It dresses an
existing `article` or `amsart` manuscript without editing its body: load
it last in the preamble and name the manuscript's theorem environments
to the apparatus —

```latex
\usepackage{atlas}                      % or [plain] for white paper
\AtlasProposition{theorem}{Theorem}[theorem]
\AtlasProposition{lemma}{Lemma}[theorem]
\AtlasDefinition{definition}{Definition}[theorem]
\AtlasScholium{remark}{Remark}[theorem]   % or Scholium, if the prose allows
\AtlasSplitTitle   % only if the title's \\ introduces a subtitle
```

— then `TEXINPUTS=path/to/latex-atlas/sty: lualatex` twice, or as
often as the original needs (a hyperref `.out` can take three). The bracket
names the counter the environment steps. A manuscript's `[T1]{fontenc}`,
`lmodern` and `amssymb` lines come out (unicode-math has the symbols;
`mathtools` may stay). The header of the file says what it sets;
`HANDOFF.md` records what dressing four real preprints taught it — seven
things from a 12-page paper, nine more from a 35-page one, nine more
from a 21- and a 19-page pair (cleveref, a subtitle after `\\`,
six-name author compounds, file names in typewriter).

On call, `\AtlasTable` prints a Table of the Propositions with real page
numbers from the `.aux` (two passes) and `\AtlasColophon` a colophon leaf
naming faces, engine, sources and revision.

`sty/atlas-grand.sty` is the other register: load it in place of `atlas`
and every costume device the lab has goes on at once — rubric, glossed
margin, initials, framed title leaf with the Table, fleurons, the hand
press and its foxed laid paper, an ornamented colophon. Three passes. It
is there to find the limit, not to post.

`sty/atlas-verse.sty` is verse over either: `\begin{poem}…\end{poem}` with
every line ending in `\\`, a `poem*` for shaped verse, `\poemtitle`,
`\attribution`, `\tailpiece`, a Contents and a sorted Index of First
Lines from the `.aux`, initials and numbers on under `atlas-grand`. A
poem measures its own lines — the widest is the block, the first is its
Index entry — and warns when a stanza runs over. `tools/verse.py` turns
plain text (`# Title`, blank lines between stanzas, indentation by spaces,
`@ attribution`, `---` for a tailpiece) into a book ready to build.
`bound/temple.tex` is its proof: four poems of Herbert's *The Temple*
(1633) as a seven-leaf chapbook — see its header for the command; three
passes. A poem may break across leaves; a block whose lines run over, or
that is wider than the measure, is warned of. The author's own
poems are dressed the way the manuscripts are: on a copy in scratch,
output to `build/`, nothing committed.

`bound/treatise.tex` gathers 07, 04 and 08 into one PDF with pdfpages,
as printed: the proof that made the seams visible and the style
necessary.

## Toward website preprints

The style above is the path. When a treatment proves itself in the lab,
it moves into `sty/atlas.sty`; preprints for `levineuwirth.org` (sources
in `~/Repos/research/meyniel`, export via `make export`) are dressed by
loading it, on a copy, with their bodies untouched. What the lab has
graduated so far: the gloss's page geometry, the apparatus of 04, the
front matter of 07, the head and measure of 08, the monochrome discipline
of 03 and 05. The frame, the lettering, 07's fleurons and imprint, and
everything in 06 are costume, and stay here. No vault (`~/universum`)
material enters this repo, and no manuscript text does either.

## License

CC BY-SA 4.0, see `LICENSE`. Third-party deps (e.g. `fiziko` if later
examples use it) are not relicensed here.
