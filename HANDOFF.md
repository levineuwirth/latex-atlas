# latex-atlas — handoff

Written 2026-09-15 at the end of the session that gave build.sh its
declared passes, biber and -j, and added the bibliography; extended
2026-09-16 by the sessions that began the graduation and dressed the
second manuscript, then the third and fourth. Read the README first; this file is what the README
does not say: why things are the way they are, what the lab has shown so
far, what bit us, and what to do next.

---

## Where it stands

`main` at `5ea3f92` (atlas-grand.sty after the third and fourth
manuscripts) plus this handoff, remote
`ssh://git@git.levineuwirth.org:2222/neuwirth/latex-atlas.git`, not
pushed. Tree clean. Eight plates, 59 PDFs from `./build.sh --ablate` in
~2 min sequential or **16 s with `-j`**; every preview byte-reproducible
from a clean build (last verified 2026-09-16 by the session that dressed
the third and fourth manuscripts).

**The graduation has begun.** `sty/atlas.sty` v0 dressed a real
manuscript — `~/Repos/research/meyniel/paper/branch-capture-paper.tex`,
`amsart`, 12 pages — with nine lines injected into its preamble and its
body untouched; the result is in `build/branch-capture-dressed.pdf`
(gitignored: no manuscript text enters this repo). See "The style" below
for the recipe and what the manuscript found. **The second manuscript**
(`near-critical-growing-radius-domination-paper.tex`, 35 pages, 2597
lines: `mathtools`, `booktabs` tables, `align`, `\keywords`, hand-set
DOIs) was dressed on 2026-09-16 by the same recipe and found nine more
things (one by the article test it prompted), all fixed in `78cfebe`.
**The third and fourth** (`ball-occupation-under-coarse-projections.tex`,
21 pages, 1817 lines, and `timed-guarding-in-degree-reduction-clouds.tex`,
19 pages, 1513 lines: both `cleveref`, a title with a subtitle after
`\\`, six-name author compounds, `\nolinkurl` file names, a `lemma*`)
were dressed on 2026-09-16 by the same recipe and found seven more, plus
two on the page and three in the grand layer, fixed in `02d7008` and
`5ea3f92`. **All four manuscripts are dressed** and their PDFs are in
`build/` (gitignored), twelve of them: `<name>-dressed.pdf` (parchment),
`<name>-plain.pdf` and `<name>-grand.pdf` for `branch-capture`,
`near-critical`, `ball-occupation` and `timed-guarding`. The recipe is
reproducible from the sources in a minute; nothing of theirs is here.

| plate | register | controls |
|---|---|---|
| 01 rubricated incipit | functional | paper, rubric, pilcrow, initial, runhead |
| 02 marginal scholia | functional | paper, margin, gloss, catchword, folio |
| 03 hatched bar chart | functional | paper, hatch, table, lining |
| 04 propositions | functional | mathfont, paper, heads, qed, scholium |
| 05 engraved graph plate | both | paper, taper, matching, stipple, frame, lettering |
| 06 hand-press impression | costume | paper, jitter, inkspread, inking, laid, foxing |
| 07 front matter | both | ligatures, paper, imprint, title, argument, table, fleuron |
| 08 bibliography | functional | oldstyle, paper, names, smallcaps, doi |

Commits so far: `69a8fec` initial three plates; `01858bd` tint notes;
`60f0dc2` the lab plus retrofits; `8171c63` plates 04–06; `af94c05` first
handoff; `c5a3983` previews in EB Garamond and the retunes; `9e12c60`
plate 07; `9aa387f` second handoff; `10debf3` review fixes (07's note
reconciled with 04, `ligatures` made a control in 07); `fda9b1a` the
build.sh decision recorded; `44293b1` build.sh implemented; `520b085`
plate 08; `0205a62` atlas.sty v0, the bound proof, the first dressed
preprint; `78cfebe` what the second manuscript found; `3996f95`,
`d1d73ca` the grand edition and its merge; `02d7008` what the third and
fourth manuscripts found; `5ea3f92` what they taught the grand layer.

## The decision

Two of them, both made deliberately:

1. **Functional and costume are both welcome.** `vintage-latex` is the
   gallery of pastiches; this repo was going to be the disciplined one,
   and the author said no: extravagance is encouraged here too. The lab
   is the instrument that lets both coexist — it shows what each device
   contributes instead of ruling on it. Do not drift back toward
   "functional only".
2. **Every modern default is an honest comparison.** The third argument
   of `\atlascontrol` is what the class, library or engine gives you when
   you do nothing: footnote for gloss, grey ramp for hatch, tombstone for
   Q.E.D., `\pagestyle{plain}` for the folio, Latin Modern Math for the
   matched math font, `\maketitle` for the title leaf, `abstract` for the
   Argument, a leadered list of theorems for the Table. Never an empty
   page or a hole. A control whose ablation is "nothing" (frame,
   catchword, laid, foxing, fleuron) is fine only when nothing *is* the
   modern default.

## What the ablations have shown

Look at `preview/ablate/` before building more; these are the findings.

- **The gloss needs the margin** (`02 --no-margin`): at a 20 mm margin
  column the note survives but chokes and overflows below the text. The
  device and the page geometry are one decision, which matters for the
  `.sty`.
- **The gloss also needs its anchors spaced.** A four-line gloss at
  `\footnotesize` pushes the next one down (`\marginparpush`) unless the
  next anchor is at least four lines below. EB Garamond sets narrower
  than Pagella, brought the anchors closer, and the cascade that had
  been a line under Pagella became obvious. Fixed by giving paragraphs
  1 and 2 two more sentences each. For the `.sty`: a gloss column is a
  constraint on the prose, not just on the page.
- **Hatch vs grey** (`03 --no-hatch`) is the cleanest single argument in
  the repo: same data, same layout, one of them photocopies.
- **The engraved lens needs heavier figures than a uniform line.** A
  lens averages far thinner than its widest point; the taper control
  uses 0.9 pt / 2.2 pt half-widths where the uniform fallback takes
  0.6 × the same figure. First attempt at 0.5 pt looked like pencil.
- **Garamond-Math beside EB Garamond is invisible in the right way**
  (`04 --no-mathfont` shows the Latin Modern mismatch: the `G`, `H`, `C`
  give it away at once). `StylisticSet={5,7}` is now understood:
  **ss05** swaps the bold math alphabet for EB Garamond ExtraBold-derived
  glyphs (ss04 would be SemiBold), **ss07** swaps the integrals for the
  upright variant. Neither touches 04 or 07, so the setting is harmless
  and right for a preprint that uses either. (Found by dumping the GSUB
  lookups with `texlua` and `fontloader.to_table`; the font names its
  sets only "Stylistic Set N".) The same math block, not as a control,
  now sits in 05 and 07 too: 05's caption `$Aa$` labels had been Latin
  Modern Math inside an EB Garamond italic caption.
- **Paper tint** ablates cleanly everywhere and every plate looks fine on
  white. 07 and 08 take 04's tint exactly, being the same book — the first
  shared tint. When the `.sty` comes, one token will do.
- **EB Garamond takes less ink than Pagella.** Its hairlines are finer
  and its x-height smaller, so 06's squash tuned on Pagella (0.09 ± 0.07
  pt) read as a semibold at 100 dpi. Retuned from a sweep at 100 and 300
  dpi: **jitter 0.24 pt, squash 0.06 ± 0.04 pt**. The per-line variation
  is still visible at 300 dpi (line 2 of paragraph 1 is a hard pull),
  and the full plate no longer reads as a weight change. Scaling by
  roughly ⅔ matched the hairline ratio between the two faces; expect to
  retune again for any other face.
- **The Table of the Propositions carries its argument by content, not
  dress** (`07 --no-table`): the list of theorems gives "3 Theorem
  (Aigner and Fromme, 1984)", the Table gives "Prop. III. Theor. II.
  *Three cops suffice upon every planar graph.*" Same page, same
  numbers. The dress (small caps, run-in italic, no leaders) is
  secondary to the statement being there at all. For the `.sty`: a
  theorem index wants the statement, which thmtools' `\listoftheorems`
  does not give without work.
- **`Ligatures=Rare`** was set in every plate but inert under Pagella.
  EB Garamond has the `ct` and `st` ties, so they are now live in 01, 02,
  04–06 (03 never asked for them): "connected", "demonstration",
  "strike". Kept as substrate there — it is the period's face — but in
  **07 it is a control** (`ligatures`, via
  `\defaultfontfeatures+[EB Garamond]{Ligatures=Rare}` ahead of the
  `\setmainfont`), because 07's plain variant is meant to be exactly an
  `article` front page and "Liſt of Theorems" with an st-tie is not.
  `07 --no-ligatures` is the comparison; a functional `.sty` will likely
  want `Rare` off, and now there is a plate to point at.
- **biblatex's default DOI and URL are the worst thing on any plain
  variant** (`08 --no-doi`, `08 --plain`): both in typewriter, the URL a
  repeat of the DOI, and the `url` package's stretchable break points
  turn "10.1016/0166-218X(84)90073-8" into "10 . 1016 / 0166 - 218X(84 )
  90073 - 8" on a justified line. Three lines per entry against two. The
  `.sty` wants `url=false` and the DOI as text whatever else it does.
- **The structure and the dress of a reference list are separable**, and
  the lab shows them separately: `08 --no-names` is biblatex's numeric
  style with small caps, old-style figures and the text DOI kept, so it
  shows what the `.bbx`/`.cbx` alone contribute (the hang, the inverted
  initials, "vol.", no quotation marks, no "In:", the head, the cite
  form). This is why the three dress controls are preamble code rather
  than bbx options: an option of the atlas bbx would be an error under
  numeric, and a bbx that carried the dress could only be *undone* by a
  control. When the style graduates, the dress moves into the bbx.
- **Old-style figures in a reference list** (`08 --no-oldstyle`): with
  lining figures every "vol. 8 (1984), pp. 1–12" stands up out of the
  line; with old-style they sit in it. The DOIs are lining in both
  variants and should be — an old-style "10.1016" reads as "IO.IOI6" —
  which is a typographic finding in itself: prose figures old-style,
  codes lining. (The review caught the plate claiming otherwise; the
  mechanism is under the gotchas.) The list is the
  densest ground of figures in a paper, which is why 08 is the plate
  where figures are a control and why the control covers the whole leaf
  (the cites carry years too). EB Garamond's *default* figures are
  lining (checked), so the modern default is honestly "ask for nothing".
- **A `.cbx` can reproduce 04's hand-set attribution exactly.**
  `\parencite{nowakowski1983,quilliot1983}` prints "(Nowakowski and
  Winkler; Quilliot, 1983)" because the cbx holds each entry's year back
  until the next entry says whether it changes. For the `.sty`: 04's
  `\begin{Theorem}[…]` attributions can become cites.
- **Three passes, not two, for a quiet biblatex log.** The page is
  complete after pass 2 (verified: pass 2 and pass 3 PNGs identical), but
  pass 2 writes `\abx@aux@defaultrefcontext` lines to the `.aux` that
  pass 1 did not, and biblatex asks to rerun. 08 declares `passes=3`
  and says why in its header.

## Re-read before touching the plates

Things that cost time once and should not cost it twice.

- **Control names are found by grep** (`\atlascontrol{[a-z0-9-]*}`),
  so never write `\atlascontrol{word}` in a comment — the README-style
  `\atlascontrol{<name>}` with angle brackets is safe. Names are
  lower-case letters, digits, hyphens.
- **The lab block is inlined in every plate, identically.** That is the
  price of standalone files. If it changes, change it in all eight.
- **`\newcommand{\foo}[1]{#1}` inside a control argument works** — `#`
  survives xparse's `+m` grabbing. Verified.
- **`\makeatletter` must sit outside `\atlascontrol`.** The argument is
  tokenised when grabbed, so a `\makeatletter` inside it comes too late
  for any `\@foo` in the same argument. 07 wraps the whole `table`
  control in `\makeatletter … \makeatother` for `\@dottedtocline`.
- **`\ignorespaces` goes after the last font switch** in an environment's
  begin code, not before it: `\itshape\ignorespaces`, or the end-of-line
  after `\begin{Theorem}[…]` survives as a space at the head of the
  statement. 04 had that in every proposition until this session.
- **`even odd rule` is a scoped option and TikZ forbids options on a
  clip path.** Put it on the scope: `\begin{scope}[even odd rule] \clip …`.
- **Don't use `remember picture`/`current page`** — it needs two runs and
  `build.sh` does one. Draw page furniture in
  `\AddToHook{shipout/background}{\put(0,0){…}}`: origin top-left, y
  negative downward, `(\paperwidth,-\paperheight)` is the far corner.
  The same one-run rule is why 07's table has hand-set page numbers and
  no `.loe`: `\@dottedtocline` is called directly.
- **Never `\today`** in a plate: the previews are byte-reproducible and
  committed. 07's modern date is the literal `15 September 2026`.
- **Lua goes in `luacode*`, not `\directlua`**, so `%`, `#` and `--`
  comments are safe. Controls then only poke numbers:
  `\atlascontrol{jitter}{\directlua{atlas.jitter = 0.24}}{}`.
- **The ink squash is a `pdf_literal` whatsit, `mode = 1`, `2 Tr w`, with
  a `0 Tr` appended at the end of the line** so headers, footers and the
  next paragraph don't inherit the stroke. Confirmed in the stream with
  `qpdf --qdf`.
- **A table line with a right-set page number** uses the ToC idiom:
  `\rightskip=2.55em plus 1em \parfillskip=-\rightskip`, then
  `\nobreak\hfill\nobreak\hbox to 1.55em{\hfil <page>}`. Without the
  `\rightskip` the statement runs under the number column and the first
  line of a wrapped entry goes loose. Scoped in a group so it does not
  leak.
- **Fonts: EB Garamond and Garamond-Math are installed**
  (`texlive-fontsextra`) and the committed previews are the Garamond
  renderings. Pagella stays as the fallback via `\IfFontExistsTF`; a
  machine without the fonts builds fine but its previews will differ
  from the committed ones, so don't commit previews from such a machine.
- **`preview/` is ~8 MB** (51 ablations at 100 dpi, 59 PNGs in all). Kept full-size so
  clicking through is worth it. If the repo grows past ~15 plates, drop
  the ablations to 60 dpi in `preview.sh` (one number) and regenerate.
- **`vintage-latex` lives in `~/scratch/tmp/vintage-latex`**, a scratch
  directory, and the README points there. If it matters — 20 plates and
  the fiziko work — move it under `~/Repos` before it gets swept.
- **Sweeping a parameter**: `sed` the value into copies of the plate in
  the scratch directory, compile each, crop with `pdftoppm -x -y -W -H`
  at 100 and 300 dpi, and `magick … -append` the crops into one stack.
  That is how 06's amplitudes were chosen; ten minutes, no guessing.
- **`%!ATLAS` lines must start the line** (`grep '^%!ATLAS …'`), so put
  them in the header next to `%!TEX program`, never indented or in prose.
  A plate that says `passes=2` and needs it will still build fine under
  `passes=1`; the difference is the output, so check the preview.
- **`-output-directory` is also searched for input.** Files a plate
  writes with `filecontents*` land in `build/` (or `build/ablate/`) and
  `\input`, `\IfFileExists`, `bibstyle=` and `\addbibresource` all find
  them there; biber does not, hence `--input-directory`. Name every such
  file under `\jobname` so parallel variants never write the same file.
- **`\usepackage[bibstyle=\jobname]{biblatex}` works**, inside an
  `\atlascontrol` argument too: LaTeX `\xdef`s the option list, so
  `\jobname` becomes the plain string before biblatex sees it.
- **`\bibstring` is not available in `\defbibheading`** (it is an
  entry-context command; "Undefined control sequence" at
  `\printbibliography`). biblatex exports only `\bibname`, `\refname`
  and `\biblistname` from its strings, so 08's bbx redefines the
  `references` string and heads the list with `\refname`.
- **`\ifcurrentname{author}`** is how a name format or a delimiter applies
  to authors and not editors: 08 uses it for the comma before "and" in
  inverted names and for the small capitals. Without it the editors came
  out "J. Koslowski, and A. Melton" and in small caps.
- **`giveninits=true` conflicts with `uniquename=full`** (biblatex warns
  and downgrades); say `uniquename=init` in the cbx.
- **A `#1` in a `\DeclareFieldFormat` inside a control argument is fine**,
  as `\newcommand` was; 08's `doi` control does it.
- **Anything set through `url` (`\url`, `\nolinkurl`) is in math mode**,
  so under unicode-math its digits come from the math font — lining, and
  out of reach of any `Numbers=` feature on the text font. 08's DOIs are
  lining for that reason (and are better for it). If a URL ever needs
  the text face's figures, it cannot go through `url`.

## Notes on 07

- The author line reads "Levi Neuwirth" — the repo's owner, on the
  grounds that the front matter is a specimen of the owner's preprint
  style, and "digested … by" claims arrangement, not the theorems.
  Trivial to change; the other plates remain anonymous.
- The Table lists eight lines: Definitions, six propositions (the three
  of 04 plus Aigner–Fromme's planar and girth results and Schröder's
  genus bound, all textbook), and the Scholium. Page numbers 1–4 are
  invented; the treatise is not on the page. **07 and 04 therefore
  disagree on numbering** — 04's Problem is Prop. III, the Table's is
  Prop. VI — and the plate's note now says so: 04 numbers its three to
  stand alone, the Table numbers the six of the whole. If 04 ever grows
  to the full treatise, the two should be reconciled.
- The imprint says "to be had at levineuwirth.org" — the period's "to be
  sold by", with the site standing in for the bookseller. It is the only
  URL in the repo and it is set as text, not a link.
- `\tableline` takes both a period head and a modern one
  (`{Scholium.}{Remark}`) because the modern list would name amsthm's
  Remark, as 04's ablation does.

## build.sh: passes, biber and -j (decided, then implemented)

Decided 2026-09-15 between the author and the reviewing session, after
weighing (a) keeping one run and hand-setting the bibliography, (b) an
explicit per-plate opt-in, (c) latexmk for everything. **(b)**, because the
one-run rule has been information, not overhead — it caught
`remember picture` and `\today` — and should stay the default with every
exception declared in the file that needs it; and because the bibliography
plate's deliverable is a biblatex style for the `.sty`, which cannot be
developed hand-set. latexmk was rejected for hiding the pass count and
adding Perl for 45 variants that don't need it.

**Implemented in `44293b1`** as specified below, and proved on 07 before
08 existed: with `passes=2` added to 07's header all nine previews were
byte-identical to the committed ones and the PDFs differed only in
`/CreationDate` and the `/ID` derived from it; the header was then
removed. Small departures from the spec as written: `-j N` is accepted
beside `-jN`; the sequential default also goes through
`xargs -P 1`, so there is one code path; `--one` takes the single
`file|job|outdir|omit` argument and exits with the compile's status;
`<job>.stdout.txt` is truncated at the start of each compile and then
appended per pass; an empty selection is not an error.

**Magic comments**, in the header next to `%!TEX program = lualatex`,
discovered by grep exactly as controls are:

```latex
%!ATLAS passes=2
%!ATLAS biber
```

- `passes=N` (default 1): `compile` runs lualatex N times with the same
  jobname and output directory. `biber` runs
  `biber --input-directory "$outdir" --output-directory "$outdir" "$job"`
  after the first pass (it reads `$outdir/$job.bcf`, finds `$job.bib` in
  the input directory, writes `$job.bbl`). Halt on the first failing
  step. Append each pass's stdout to `$outdir/$job.stdout.txt`; send
  biber's to `$outdir/$job.biber.txt` (it also leaves `$job.blg`).
- Variants inherit the plate's passes and biber: `-jobname` already keeps
  every variant's `.aux`, `.bcf`, `.bbl` apart, so nothing else changes.
  A variant whose control turns the bibliography off still runs the extra
  passes; harmless, and the plate says `passes=2` on purpose.
- The **`.bib` lives inside the plate** in a `filecontents*` block, so the
  file stays standalone (a stated invariant) and each variant writes its
  own copy:

  ```latex
  \begin{filecontents*}[overwrite]{\jobname.bib}
  @article{...}
  \end{filecontents*}
  ...
  \addbibresource{\jobname.bib}
  ```

  `filecontents*` works before `\documentclass`; with `-output-directory`
  the `\openout` lands in `$outdir`, which is why biber needs
  `--input-directory`. Expect biblatex's "Please (re)run Biber" warning
  after pass 1; `-halt-on-error` ignores warnings.
- **`-j N`**: `./build.sh -j4 --ablate`; bare `-j` means `nproc`. Default
  stays sequential so output order is stable. POSIX sh has no exported
  functions, so build the job list as lines (`file|job|outdir|omit`),
  pipe to `xargs -P N -L1 ./build.sh --one`, and let `--one` call
  `compile` and print its own `OK`/`FAIL` line. Tee the lines to a temp
  file; the summary greps `^FAIL` from it and exits 1 if any (xargs
  itself returns 123). A bibliography plate with five controls is
  7 variants × (2 lualatex + biber) ≈ 21 processes, ≈ +15 s sequential;
  `-j` is the answer if the full build ever stops feeling free.
- **Reproducibility is unaffected**: biber's `.bbl` is deterministic for
  a given `.bib` and version, and pass 2 reads only what pass 1 wrote.
  Verify as before — clean build, `./preview.sh`, clean tree — before
  committing the first two-pass plate's previews.
- What this does not buy: 07 stays hand-set. A second pass only reads
  numbers that exist on the page, and 07's treatise is not on it.

## Notes on 08

- Five controls, but not the five the previous handoff proposed:
  `hanging` and `urls` became `names` and `doi`. A hang without a label
  is what every unlabelled list has, so "no hanging" has no honest
  default; the honest comparison is the numeric style whole, labels and
  cites together, and that is `names`. `urls` was named for the wrong
  side ("without urls" would *add* them); `doi` is the treatment, the
  identifier as a word of the text.
- `initials` (inverted names cut to initials against "Martin Aigner and
  Michael Fromme") and roman volume numbers ("vol. viii.") were
  considered and left out: the first is structural and lives in the bbx,
  the second is costume that would earn a variant only if someone wants
  it. Either would be a ten-minute control.
- The bbx keeps the year after the journal, "vol. 8 (1984)", not the
  Royal-Society form with the year after the names. With author-year
  cites the latter is arguably more logical; it is one macro
  (`author/editor+date` from `standard.bbx`) if the author wants to try
  it.
- Small caps are on the author's family name only, in the list only; the
  text's cites stay in the text face as 04's attributions do. With
  `\textls[50]`, as every small-cap line in the repo is tracked.
- 08 follows 07's numbering of the six propositions (the Problem is
  Prop. VI.), not 04's; the plate says so.
- Quilliot is the 1983 thèse d'État, which is what 04's "Quilliot, 1983"
  points at; his 1978 thèse de 3e cycle has the same result and is
  what some texts cite. Frankl (1987) is where Meyniel's Problem was
  first printed; Meyniel himself has no entry, as the handoff asked.
- The three `filecontents*` blocks use `[overwrite,nowarn]`, not the
  spec's `[overwrite]` alone: `nowarn` only silences "file exists,
  overwriting" on the second and third pass.

## The bound proof

`bound/treatise.tex` gathers 07, 04 and 08 as printed (pdfpages; build
the plates first, then `lualatex -output-directory=build bound/treatise.tex`).
Turned on 2026-09-16, it showed that the *design* coheres without a
shared file — one stock, one text block, one voice for every head,
matched faces — and that every seam is an artefact of the plates standing
alone: the title set three times (04 and 08 restate it), no folios, no
running heads, the lab stamp on every page, and the numbering fork (04's
Problem is Prop. III, the Table's and 08's is Prop. VI). That list is
exactly what a shared style produces once, which is why the graduation
moved to the front of the queue. The fleuron band appears on 07 only; a
book would want the tailpiece on 08 too.

## The style: `sty/atlas.sty` v0

Lifted from the common preamble of 04/07/08, plus what the bound proof
said was missing. Load it **last** in the preamble, after the manuscript's
`\newtheorem`s and after hyperref; then name the manuscript's theorem
environments to the apparatus. Options: `plain` (white/black, for arXiv
and print — tested), `rareligatures` (default off, per 07).

What it sets: EB Garamond + Garamond-Math (Pagella pair fallback),
old-style figures, the 04/07/08 stock and ink, their A4 geometry, spaced
small-capital section heads (subsections display-style, italic), a title
leaf after 07 (title in spaced capitals, "by", address, date, double rule,
then *The Argument* in place of the abstract — boxed as `amsart` boxes the
abstract, so the source order abstract-before-`\maketitle` is kept), the
apparatus of 04 (centred head, attribution beneath, italic statement,
*Demonstration*, Q.E.D.), run-in definitions and remarks, a running head
under a hair rule, a centred folio, and 08's *The Authorities* head and
small type for whatever list the manuscript sets. Not in v0: 08's
biblatex `.bbx`/`.cbx` (this manuscript hand-sets its bibliography, so
only the head and size are dressed), rubrication, the lab controls.

**The recipe** (what was done to `branch-capture-paper.tex`, on a copy in
scratch — never in the research repo):

```sh
cp ~/Repos/research/meyniel/paper/branch-capture-paper.tex work.tex
# 1. remove \usepackage[T1]{fontenc}   (and \usepackage{lmodern} if present:
#    the second manuscript had it; the same pdflatex-only pair)
# 2. amsmath,amssymb,amsthm -> amsmath,amsthm   (unicode-math has the symbols;
#    mathtools stays, the sty silences unicode-math's two notes about it)
# 3. before \begin{document}:
#    \usepackage{atlas}
#    \AtlasProposition{theorem}{Theorem}[theorem]
#    \AtlasProposition{lemma}{Lemma}[theorem]
#    \AtlasProposition{proposition}{Proposition}[theorem]
#    \AtlasProposition{corollary}{Corollary}[theorem]
#    \AtlasProposition{question}{Question}[theorem]
#    \AtlasDefinition{definition}{Definition}[theorem]
#    \AtlasScholium{remark}{Remark}[theorem]
#      -- or {Scholium}, the author's preference for the dressed editions,
#         ONLY where the prose never writes "Remark~\ref" (grep first: of
#         the four, only timed-guarding qualifies today); with cleveref add
#         \crefname{remark}{Scholium}{Scholia} so \cref says it too. The
#         canonical sources keep Remark.
#    \AtlasSplitTitle    where the title's \\ introduces a subtitle or a
#                        qualifying clause (ball-occupation, branch-capture);
#                        a \\ that breaks a phrase mid-way flows (near-critical)
#    \AtlasScholium{remark*}{Remark}
TEXINPUTS=~/Repos/personal/latex-atlas/sty: lualatex work.tex   # twice
```

The bracket is the counter the environment steps (the shared one for
`[theorem]`-style sharing); without it the environment is unnumbered (a
`\newtheorem*{lemma*}` is `\AtlasProposition{lemma*}{Lemma}`). Run it
as many times as the original needs: the third manuscript's `.out`
changes on the second pass under pdflatex too, so it takes three.
Output: 13 pages A4 against the original's 12 letter (12 since the node
renderer, below), zero warnings, every number and cross-reference
identical to the `amsart` build.

**What the manuscript found that eight plates could not.** Each is fixed
in v0 and each is a gotcha for anything built on the same pieces:

- `\refstepcounter` inside `\centerline` (or `\textls`) sets
  `\@currentlabel` locally; the counter advances but `\label` records the
  enclosing section. "Lemmas 2 and 2 give" was the tell. Step the counter
  before the head, outside every box and group. The plates never
  `\label`ed anything.
- A run-in subsection directly before a theorem is deferred by
  `\everypar` into the statement's first line. Subsections are
  display-style for that reason.
- `\lsstyle` in a `\@startsection` style argument swallows `amsart`'s
  `\enspace` after the section number, and is redundant: `tracking=true`
  already letterspaces the `sc` shape at the `\SetTracking` amount.
- A manuscript's hand-placed `\\` in `\title` was set for its own class;
  in spaced capitals the title is let to flow. `center` redefines `\\`, so
  the neutralising `\def` must sit inside it, at the title.
- `\label` on the line after `\begin{theorem}` leaves a stray space
  unless the head ends in vertical mode with `\@afterindentfalse
  \@afterheading`, as a section head does; `\noindent\ignorespaces` is not
  enough because `\@esphack` re-arms `\ignorespaces` only after glue.
- `amsart` repeats the addresses after the references
  (`\@setaddresses`); the title leaf has already given them.
- **Captions are content.** Renaming *Remark* to *Scholium* in the dress
  broke line 552, which says "Remark~\ref{...}". A style takes the
  manuscript's captions as given; the period word is the author's
  decision in the source. 04 may say Scholium because 04 is the source.

**What the second manuscript found** (2026-09-16, the same recipe with
`lmodern` also removed; 36 pages A4 against 35 letter, zero warnings, all
141 `\newlabel`s and 16 `\bibcite`s identical to the `pdflatex` build in
both editions; the first manuscript re-dressed afterwards as a regression
check is now 12 pages against its 12, zero warnings, 17 labels identical).
Each fixed in `78cfebe`:

- **HarfBuzz cost protrusion and expansion, and nobody had chosen it.**
  Every plate says `Renderer=HarfBuzz` and
  `protrusion=false,expansion=false` because 01 did, and no comment or
  commit says why. The manuscript set eight overfull lines, up to 17 pt,
  on the 402 pt measure — long inline formulae that pdflatex's Latin
  Modern absorbed with expansion. Under `Renderer=Node` with both on:
  none, same page count, and the title leaf compared under both renderers
  keeps tracking, small capitals, old-style figures and the ct/st ties.
  The sty is on the node renderer; the plates are not (eight files and
  every preview), see Outstanding.
- **Garamond-Math lacks 54 of unicode-math's symbols, and a missing glyph
  is a log line, not an error.** The manuscript's four `\sharp`s came out
  as nothing. Found by setting every command of `unicode-math-table.tex`
  (accents with an argument, one `\par` per line — the "Missing
  character" lines are logged at the paragraph, so one paragraph per
  symbol is what makes them attributable) under each font and reading the
  logs: the ≗ ≜ ≝ family, the card suits, the accidentals, ⪋ ⪌ ⪕ ⪖,
  the checkmark, the maltese cross, five bold sans-serif Greek. All in
  Pagella Math, so `\setmathfont{TeX Gyre Pagella Math}[range={…}]`
  after the main font. luaotfload's `fallback=` feature was tried first
  and does not reach math fonts. A `fontloader.to_table` cmap dump was
  tried before that and lied (it missed the alphabet letters the font
  reaches through alternate unicodes): the engine's log is the only
  ground truth for coverage.
- **`mathtools` before `unicode-math` gives two warnings at
  `\begin{document}`** — mathtools keeps `\overbracket`, unicode-math
  takes `\coloneqq` and three siblings. Both are unicode-math's decisions,
  made because the sty loaded it; `warnings-off={mathtools-colon,
  mathtools-overbracket}` by `\PassOptionsToPackage`.
- **`\maketitle` dropped amsart's first-page footnotes.** `\keywords`,
  `\subjclass` and `\thanks` go to the foot of page 1 unmarked, through
  `\@adminfootnotes`; v0's leaf printed none of them. Now set as amsart
  sets them, minus the date, which the leaf gives. article's `\thanks`
  (symbol marks in the author line, `\@thanks` after) go through too.
- **hyperref wraps `\maketitle`** to run the *unpatched* footnote
  commands inside it, because its footnote anchors need a mark these
  footnotes never get. `\renewcommand{\maketitle}` threw that wrapper
  away, and the first keywords footnote warned "Ignoring empty anchor".
  Do what the wrapper did: `\let\@footnotetext\H@@footnotetext` inside
  the group.
- **No space after the Argument.** amsart's `\@maketitle` ends with
  `\vskip 34pt−\baselineskip` after the abstract; v0 ended with the box.
  The first manuscript hid it — its body opens with `\section`, which
  brings its own space — the second opens with a `\noindent` paragraph
  and ran straight on from the abstract's last line.
- **article's order never printed the Argument.** `\maketitle` then
  `abstract` fills the box after the only place that emptied it. As amsart
  does for a late abstract, `\end{abstract}` now sets it when
  `\maketitle` has already run. (Found by the article test for `\thanks`,
  not by the manuscript; the sty claims article.)
- **`\href` text is text.** The manuscript hand-sets its DOIs as
  `\href{https://doi.org/…}{10.1016/…}`, and the link text took the
  old-style figures: "IO.IOI6", the very thing 08 recorded. 08's own DOIs
  escaped only because `\url` sets its digits in math mode. The driver's
  `\hyper@linkurl{text}{url}` is the one place `\href` and `\url` both
  pass through, so the sty wraps it: the text of an external link takes
  lining figures. Prose and internal `\ref` links are untouched; a link
  text of words has no figures to change.
- **A table's figures are lining and tabular** (03's rule) in every
  `tabular`, `tabular*`, `tabularx`, `longtable`, by an `env/…/begin`
  hook. The manuscript's diagnostic table has an `h` column of integers
  in text beside three columns of values in math: old-style proportional
  beside lining tabular in one table, until this.

Seen and left alone, as the manuscript's own: amsart's `\paragraph` is
`\normalfont` run-in with no space above, so "Act I: …" is invisible as a
head in the original too. The sty voices `\section` and `\subsection`
and not `\paragraph`; whether it should (italic run-in, after 04's
scholia) is a register question, with the caveat in the first list that a
run-in head before a proposition is deferred into the statement.

**What the third and fourth manuscripts found** (2026-09-16, the same
recipe, three passes; 21 pages A4 against 21 letter and 20 against 19,
zero warnings, zero missing characters, no overfull line in either
edition against the originals' none; every `\newlabel` and `\bibcite`
— 94 and 119 entries — agrees with the pdflatex build in number, name,
anchor and cleveref type, the page field excepted, in both editions; the
first two manuscripts re-dressed afterwards are 12 and 36 pages as
before, clean, labels identical). Each fixed in `02d7008`:

- **cleveref and nameref read amsthm's `\@thm`, and the apparatus
  bypasses it.** cleveref's own amsthm patch calls
  `\refstepcounter[lemma]{theorem}` so a shared-counter environment is
  typed by its name; nameref's patch of `\@begintheorem` calls
  `\NR@gettitle{name}` so `\nameref` gives the theorem's name, and the
  third field of every theorem's `\newlabel` carries it. The apparatus
  did neither: the first two manuscripts' `.aux` diffs had the section
  title in that field (the previous thread compared numbers and anchors
  and did not see it). `\atlas@step{env}[counter][name]` now does both,
  each only if its package is loaded. **Not the style's, but the
  author's to know:** TeX Live 2026's kernel first-aid for cleveref
  (`latex2e-first-aid-for-external-files.ltx`, `label` hook) re-derives
  the label type from `\@currentcounter` at every `\label`, so under
  amsart *and* under article, original or dressed, `\cref` of a lemma
  that shares the theorem counter says "Theorem 4.1". The two
  manuscripts `\cref` only theorems, sections, equations and items, so
  nothing shows; a `\cref{lem:…}` would. Reproduced in eight lines:
  amsart or article, amsthm, cleveref, `\newtheorem{theorem}{Theorem}
  [section]`, `\newtheorem{lemma}[theorem]{Lemma}`, a lemma with a
  `\label`, `\cref` of it. Upstream.
- **A title's `\\` is a subtitle as often as a line break** — and a style
  cannot tell which. The first manuscript broke its title for amsart's
  measure; the third names a subtitle after its `\\`, and flowing ran
  "…Coarse Graph Projections Degree Reduction, Square-Root Hard
  Families…" into one title. The thread that found it split every title
  at the first `\\` (capitals, then italic beneath, as 07's "or," line);
  the review counted: of three titles with a `\\`, two were line breaks,
  and the second manuscript's capitals ended on "FOR". So the split is
  now **`\AtlasSplitTitle`, a declaration in the injected preamble**, and
  the default is to flow in balanced capitals. The person injecting the
  nine lines can see which the author meant; the recipe below says so.
  Applied: ball-occupation split, the other three flow (near-critical in
  three lines breaking at phrase boundaries, thanks to the finite-stretch
  centring found in the same round).
- **Centred capitals with fil stretch leave one word on the last line.**
  "TIMED GUARDING IN DEGREE-REDUCTION / CLOUDS": with `\centering`'s fil
  every line is equally good and TeX fills the first. The title paragraph
  now has finite stretch at either side (`0pt plus .5\hsize`, `\parfillskip`
  zero), so a short last line costs badness and the lines balance:
  "TIMED GUARDING IN / DEGREE-REDUCTION CLOUDS". The interword spaces take
  a share of the stretch in proportion to their own, which is small; it
  does not show.
- **TeX breaks after a hyphen and never after an en dash.** The empty
  discretionary TeX inserts after `\hyphenchar` is the only such
  break; a six-name compound (Bose–Esperet–Hodor–Joret–Micek–Rambaud)
  is one unbreakable word of 150 pt, and on the 402 pt measure the
  paragraph had no feasible first line — 42 pt overfull. pdflatex's 469 pt
  measure hid it (the same paragraph, no break either, fitted). A node
  filter in `pre_linebreak_filter`, registered after luaotfload's so it
  sees the dash luaotfload made from `--`, puts a penalty of
  `\exhyphenpenalty` after an en or em dash that stands between two
  letters (`\lccode` nonzero on both sides, kerns skipped); a dash beside
  a figure or a space is left alone. Four of the eight overfull lines
  were this.
- **`\emergencystretch` is zero in amsart, so a mathematical paragraph
  gets no third pass.** An inline formula of 100 pt before its full stop,
  the line that ends at "with" 60 pt short: no feasible break at
  `\tolerance` 200, and TeX sets the overfull line rather than the loose
  one. 2 em is set: the smallest of 1, 1.5, 2, 2.5, 3, 4 em that set both
  manuscripts without an overfull line (1 and 1.5 leave one; from 3 em,
  paragraphs that had set well come out loose — two underfull at 3, four
  at 4; `\sloppy` is 3 em). The one line it rescues is logged
  `Underfull \hbox (badness 1755)`, as it should be: a formula half the
  measure, set inline, is the author's to display.
- **url's default breaks a file name after its full stop and not at its
  hyphens.** `\nolinkurl{hmghm-exterior-tree-setup.py}` broke as
  "…setup." / "py" in the original too (url's `\UrlBreaks` has the stop,
  `\UrlBigBreaks` has `\do@url@hyp`, empty unless the `hyphens` option
  was given, and hyperref has loaded url before the sty can pass it).
  The option is the one definition `\def\do@url@hyp{\do\-}`, made if
  url is loaded. The classic objection — a hyphen at a line end is
  ambiguous in a URL — is noted and outweighed on this measure.
- **The manuscript's typewriter read a size larger.** fontspec's default
  `\ttfamily` is Latin Modern Mono at nominal size; beside EB Garamond's
  small lowercase it was visibly bigger, and a paragraph of file names set
  two overfull lines of it (28 and 60 pt). `\setmonofont{Latin Modern
  Mono}[Scale=MatchLowercase]` — the face is not changed, only sized to
  the text face's x-height, as fontspec provides for. Whether `\url`
  should leave typewriter at all stays an open register question.

And two from the page, not from the log:

- **amsart's `\footskip` is 12 pt** and geometry keeps the class's value
  unless told: the folio sat a line and a half under the last line of a
  full page, in the first two manuscripts as well, unremarked. `footskip=8mm`
  is named, the headsep's mirror.
- **The Argument was a box.** amsart boxes the abstract so that the
  source order abstract-before-`\maketitle` works, and v0 did the same;
  a box cannot break across pages. Found by the grand layer (below), fixed
  in atlas: `\unvbox`, not `\box`. The Argument is prose.

Seen and left alone: the third manuscript's bibliography hand-sets three
arXiv numbers as `\href` (lining, by the link-text rule) and three as
plain text (old-style, by the prose rule), in one list; a rule that
reaches prose would be pattern-matching, and the real answer is 08's
`.bbx`, where the identifier is a field (Outstanding, below). Both
manuscripts' `\section*` heads, `enumerate` labels, `\boxed` displays
and `lemma*` came through as the manuscripts set them.

**To judge, not yet judged:** the reading experience — 12 and 36 pages of
11 pt EB Garamond on parchment is a denser, quieter page than `amsart`'s.
Whether that is right for a preprint is the author's call. The `plain`
edition exists for the other answer.

## The grand edition: `sty/atlas-grand.sty`

Built 2026-09-16 on a branch while the second manuscript was being
dressed, then merged. It loads `atlas` and lays every costume device the
lab has over a running manuscript at once, to see where the limit is: the
rubric red (01), 02's broad outer margin with the propositions' names
glossed in it, a dropped initial after every section head (01), a framed
title leaf of its own (05) carrying the Argument, the Table of the
Propositions, fleurons and the imprint (07), roman section numerals, a
fleuron before every section, 06's press and sheet under every page, and
ornaments on the colophon. Load it in place of `atlas`, same recipe, three
passes; `\AtEndDocument{\AtlasColophon}` for the last leaf. Nothing in it
is for a preprint one would post. Outputs: `build/branch-capture-grand.pdf`
(15 pp), `build/near-critical-grand.pdf` (40 pp: the 44-entry Table runs
the framed front matter onto a second leaf).

**What moved down into `atlas.sty` at the merge**, being functional:

- `rubric` is a colour token in `atlas.sty`, **equal to ink** — plate 01's
  own ablation — and every head, rule and running head is set in it, so a
  layer turns the whole apparatus red with one `\definecolor`.
- `\AtlasTable`: every `\AtlasProposition` environment writes kind, number,
  name and page to the `.aux`; `\AtlasTable` prints them under 07's head
  with real pages on the second pass. Nothing prints unless called. This
  is what 07 could only hand-set.
- `\AtlasColophon`: a last leaf naming faces, LuaTeX version, sources and
  revision (`\atlasrevision`, `\atlassources`, `\def`'d on the command line
  — no shell escape). Plain rules in `atlas`; the grand layer swaps in
  ornaments and adds its sentence on the sheet through two hooks.
- The title leaf is in pieces — `\atlas@titleblock`, `\atlas@titleleaf`,
  `\maketitle` — so a layer arranges the leaf without repeating the
  footnote and hyperref handling the second manuscript added.

**What stays in the grand layer**, being costume or needing its geometry:
the margin gloss (needs 02's page), the initials, the frame, the fleurons,
the imprint, roman numerals, the press and the sheet.

**Review findings on the third round**, gotchas now:

- amsart declares the document's first page `plain` at class load; its own
  `\maketitle` overrides that with `firstpage`. The `atlas` leaf's
  `\thispagestyle{empty}` beats it; the grand leaf had switched to
  `\pagestyle{empty}` for its continuation leaves and so carried a bare
  folio "1" under the footnotes on both grand editions for a round. Both
  are set now.
- `build/` holds the dressed manuscripts, and `preview.sh` rendered
  every `build/*.pdf` — twelve manuscript PNGs appeared in `preview/`,
  untracked, one `git add -A` from the repo. `preview.sh` now matches
  `build/[0-9][0-9]-*.pdf` only. The rule stands: nothing of a manuscript
  reaches a committed path.

**Five things it taught**, all gotchas now (the last three from the
third and fourth manuscripts, fixed in `5ea3f92` and `02d7008`):

- `cmd/section/after` hooks fire *before* a `\@startsection` command
  reads its argument; `\section` and `\subsection` are wrapped with
  `\RenewDocumentCommand{...}{s o m}` instead.
- A `\futurelet` inside `\if…\fi` peeks at its own `\fi`; the peek runs
  after `\expandafter` has removed the conditional. (The initial mechanism
  peeks at the first token of the paragraph after a section head, grabs
  the word if it is a letter, steps over a leading `\label`, and disarms
  quietly on anything else.)
- **A dropped initial needs its three lines with the head.** LaTeX keeps
  one line of the paragraph with a section head; a head two lines from
  the foot hung its initial below the page — lettrine's "ATTENTION
  REQUIRED", twice in each manuscript. The section wrapper now
  `\needspace{8\baselineskip}` first (fleuron and its space, head and
  its skips, the initial's three: six was too few, and left the fleuron
  alone at the foot), and raises `\@secpenalty` for the head that follows
  a fleuron, since that penalty (−300) invites the page break between
  them. Requires `needspace`.
- **The Argument as a box does not fit the framed leaf** once the grand
  measure (370 pt) has made a long one longer: it went whole to the second
  leaf and left the first underfull (badness 10000) with the title block
  and footnotes alone on it. Unboxed in atlas.sty, it breaks across the
  leaves as prose. amsart's abstract has the same failure.
- **The front-matter leaves are flush-bottom**, as the class is, and a
  middle leaf of Table lines has nothing to stretch: underfull. `\maketitle`
  sets `\raggedbottom` while the leaves last and restores `\@textbottom`
  after the `\clearpage`; the last leaf has its `\vfill` before the
  imprint anyway.

Smoke test after these, three passes each with `\atlasrevision` and
`\atlassources` on the command line: ball-occupation 25 pp, timed-guarding
23, branch-capture 15, near-critical 40; no warnings, no missing
characters. Left as the measure's own: two overfull lines of 2.5 pt
(one a display) in ball-occupation and a display 12 pt wide in
branch-capture on the 370 pt gloss measure, one loose line in
timed-guarding (badness 1082), and one loose page where ball-occupation's
bibliography breaks (badness 1019). A display is the author's width;
the grand measure is 02's.

**Judgement recorded:** the *type* devices — initials, rubric, glossed
margin, the Table, the colophon — read as a designed book; the *sheet*
devices — foxing, laid lines, ink squash — read as a facsimile, and on a
screen a foxing spot beside a formula looks like dirt. That is where the
limit is: the grand edition is at its best exactly where it stops
pretending to be old paper.

## Verse: plate 09, `sty/atlas-verse.sty`, `bound/temple.tex`

Begun 2026-09-16 at the author's turn toward poetry, with the grand
register as the destination: the author's own poems, eventually, dressed
as the manuscripts were — on copies in scratch, output to `build/`,
nothing committed, and nothing from `~/universum` ever read into this
repo. The lab text is Herbert's *The Temple* (1633), public domain, in
its spelling.

**Plate 09** isolates what verse needs and prose does not: the block
centred on its longest line (against the class's `verse`, which indents
at the margin), a two-line initial, the title in small capitals, every
fifth line numbered at the block's edge, the source set right, a
tailpiece; `rubric` and `paper` as always. Eight controls; the indented
short lines are Herbert's and stay in every variant.

**The block** is the plate's own, not `verse.sty`'s (not installed here —
`texlive-humanities` — and it would replace the kernel's environment,
which is the honest default). Convention: **every line ends with `\\`**,
stanzas are separated by a blank line, a stanza is one paragraph. `\\`
counts the line, sets its number, and either breaks the line or, seeing
the `\par` a blank line leaves (`\@ifnextchar\par`), ends the stanza and
sets the stanza space itself. First lines are outdented by a negative
`\parindent`; run-overs keep the `\leftskip` hang; `\vin` indents a
line; `poem*` centres every line for shaped verse (*Easter Wings*).

**What it cost to learn**, gotchas now:

- **Any user `\everypar`, even `\relax`, loses the `\parskip` between
  paragraphs inside a minipage** under the 2021+ kernel (tested: cases
  A–G in scratch). The block therefore has no `\everypar`; the stanza
  space is explicit and `\parskip` is zero.
- **Glue at the head of a line after a forced break is discarded**, so an
  outdent after `\newline` needs a `\null` before it.
- **lettrine issues its own `\par` and `\noindent`**, which throw away
  anything set before it at paragraph start; in a `\leftskip` block its
  first line came out 1.5 em short and wrapped after one word. The initial
  is by `\hangindent`/`\hangafter=-2` instead, sized by measurement
  (`\fpeval`) so its cap height spans two lines, set on the second line's
  baseline; it composes with the block's outdent on every line.
- **`\stanzaskip` cannot be set from `\baselineskip` in the preamble**
  (zero there); it is measured at `\begin{poem}`.
- **What Lua `tex.print`s is read with the document's catcodes**, where
  `@` is not a letter: "@havefirstlines" appeared on the page. The two
  names Lua hands back are `@`-free (`\verseTableEntry`,
  `\verseHaveFirstLines`).
- **`atlas.sty` renewed `\proofname` and `\qedsymbol` unconditionally**;
  the first non-amsthm document broke on it. Both are `\providecommand`ed
  first now.
- An end-of-line space inside `\ifnum … \llap{…}\fi` shifted every
  numbered line by a word space; `\relax` closes the number.

**The verse review** (the other thread reviewed this session's work,
2026-09-16 — the roles reversed, and the loop caught the same kind of
thing it always has), seven findings, all applied:

- **Overflow is silent under ragged right.** Two `\poemblock` lines in
  `temple.tex` named the wrong longest line; four lines of *Prayer* and
  the first of *Easter Wings* ran over and read as intentional indents,
  and "zero warnings" saw nothing. Now `\\` counts the stanza's lines and
  after its `\par` compares `\prevgraf` (the lines TeX set) with the
  count; the difference is a `\PackageWarning`. **`\prevgraf` reads 0
  inside `\write`** (TeX's mode is 0 there), so it goes into a count
  first. Tested: 2/1/1/1 on the narrow block, 0 on the right one.
- **A `\\` before `\end{poem}` made an empty last line** — one
  `\baselineskip` of air under every poem, in the plate too. `\\` now
  peeks for `\end` as it peeks for `\par`.
- **fancyhdr freezes `\headwidth`** at the measure in force when
  `\pagestyle{fancy}` is said. atlas says it at 142 mm; grand then narrows
  the block to 130 mm, and every grand page since the first merge had its
  head rule overhanging the outer margin and head and folio 6 mm off the
  block's axis — the twelve dressed editions included. `\fancyhfoffset{0pt}`
  after grand's `\geometry`. Three rounds of looking missed it.
- **A control word eats the space after it**: `\atlas@colophon@sheet`
  followed by a newline gave "order.The propositions" in every grand
  colophon. The sheet sentence ends with `\space`; atlas prints the two
  hooks with nothing between.
- The colophon's "on `\@date`" was the poems' date (1633); a
  `\atlas@colophon@when` hook, `\atlassetdate` in verse (default
  `\today`; `\def` it on the command line for a reproducible book).
- **The block is no longer a minipage**, so a poem can break across
  leaves: ordinary paragraphs centred by `\leftskip`/`\rightskip` at
  `(\linewidth-\poemwidth)/2` (plus the hang on the left), stanza ends
  the natural break, `\interlinepenalty` holding a stanza. A block wider
  than the measure is set at the measure with a warning. Plate 09 keeps
  its minipage — a one-page specimen — and says so.
- **`\newlength` makes a skip register**, and `\rightskip<skip>\@plus1fil`
  takes the register as the whole glue and typesets "plus1fil" — found
  while applying the block change, when the checker fired on the *right*
  widths: the lines were justified and wrapping. `\newdimen` for the offset.
- Also: a one-word first line ("Lord,\\") had its `\\` swallowed into the
  initial's small capitals — the grab now splits at `\\` and puts it back;
  the attribution hangs on the block, not the measure; `poem*` takes no
  numbers (a fill-glue number would break its centring), documented; 09's
  no-block default is now the class's own `\leftmargini`, not 1.5 em.

**`atlas-verse.sty`** loads over `atlas` or `atlas-grand`: `poem`/`poem*`,
`\poemblock`, `\poemtitle` (recorded for the Contents), `\attribution`,
`\tailpiece`, `\AtlasContents`, `\AtlasFirstLines` (sorted in Lua, with
articles set aside, as an index does), `\AtlasPoemsOnNewPages`,
`\AtlasVerseInitials`, `\AtlasVerseNumbers{n}`; under grand the initials
and numbers are on and the Contents join the title leaf. The initial is
automatic: the poem's first token is peeked (spaces eaten first, one at a
time) and, if a letter, its word is opened with `\incipit`.

**`bound/temple.tex`**: *Vertue*, *The Pulley*, *Prayer*, *Easter Wings*
as a seven-leaf chapbook in grand — framed title leaf with the Contents,
a poem to a leaf, Index of First Lines, colophon ("this edition of the
poems"). Zero warnings, three passes. `build/temple.pdf`.

**To the author's poems**: the recipe is the manuscripts', shorter. A
copy of the poems in scratch as a LaTeX file — `\poemtitle`, `\poemblock`
with the longest line, `\begin{poem}[first line]`, lines ending in `\\`,
blank lines between stanzas, `\vin` where a line is indented — with
`\usepackage{atlas-grand}\usepackage{atlas-verse}` and the four lines of
`temple.tex`'s preamble; `TEXINPUTS=sty:`, three passes, output to
`build/`, with `\def\atlasrevision{…}\def\atlassetdate{…}` on the
command line as `temple.tex`'s header shows. Measure each `\poemblock`
line honestly — the style now warns when one is too short. Grandness per instance: `\AtlasVerseNumbers{0}` for no numbers,
plain `atlas` beneath for a quiet edition, and the per-device grand
options still to be built.

## Outstanding, in rough order

The graduation is the main line now; the lab continues beside it in
both registers. Verse joined it on 2026-09-16 (plate 09, `atlas-verse`,
the Herbert chapbook), and the author's poems are its destination.

0. **The author's poems, dressed** — the recipe is under "Verse"; on a
   copy in scratch, nothing committed. The first real book will find what
   Herbert's four leaves did not (long poems across pages, epigraphs,
   dedications, dates under poems, sections within a book, a poem whose
   longest line is longer than the measure — the last two are handled
   now, untested on a real book). Fix generically in `atlas-verse.sty`;
   record as the manuscripts' findings are recorded.
0a. **Per-device grand options** (`nosheet`, `noinitials`, `noframe` …),
   so that grandness is a scale an instance sets, as decided.

1. **The register questions are decided** (author, 2026-09-16, after
   reading all twelve editions): *parchment is the site edition*, `plain`
   for arXiv and print; density stays; `\paragraph` is run in italic (in
   the sty); `\url` takes the text face (in the sty); plain-text arXiv
   numbers in a hand-set bibliography are the author's to wrap in `\href`
   so they take lining figures like the DOIs beside them; *Scholium* is
   wanted in the dressed editions where the manuscript's prose permits it
   (the canonical sources keep Remark) — see the recipe; branch-capture's
   title splits as well as ball-occupation's; rare ligatures stay off;
   grandness is a scale for each instance to set, not a binary, so the
   grand layer keeps every device. Remaining for the author, in the
   research repo: the arXiv numbers, and "Remark~\ref" → `\Cref` (or the
   word) in the three manuscripts whose prose names the kind, which is
   what stands between them and Scholium.
2. **Tell the author about cleveref.** Under TeX Live 2026, `\cref` of a
   lemma sharing the theorem counter says "Theorem", in the pdflatex
   originals as much as in the dress (the kernel first-aid, above). None
   of the four manuscripts does it yet.
3. **The plates are on the node renderer** with protrusion and expansion,
   as the style is (author's decision; one commit, all 59 previews
   regenerated, byte-reproducible, zero warnings).
4. **08's biblatex style into the `.sty`** as `atlas.bbx`/`atlas.cbx`
   with the dress moved in from 08's preamble — the first manuscript
   whose bibliography is a `.bib` will want it. Then `\cite` in a dressed
   manuscript can become name-and-year without touching its body.
5. **Errata slip** as revision notes — the colophon exists now
   (`\AtlasColophon`); the slip is the remaining half. Keep distinct from
   07's imprint (imprint = title leaf, colophon = last leaf).
6. **Fold-out plate** — a landscape leaf for a wide table; the longer
   manuscripts may need it.
7. **Marginal figures** — small graph drawings in the scholia margin, the
   natural sequel to 02 + 05.
8. **Should the `.sty` carry lab controls** so a dressed preprint can be
   ablated? Cheap to add (the block is eight lines) and it would let the
   register questions in 1 be answered by looking rather than arguing.
9. **CSS counterparts for the Hakyll site.** Separate repo when it happens.

The `treatise.tex` sample document proposed after the bound proof (04
grown to its six propositions) is no longer needed: a real preprint is
the sample now. 04, 07 and 08 stay as lab plates; the numbering fork
between them stands, documented in 07's note.

The site export path is unchanged: sources in `~/Repos/research/meyniel`,
`make export` to `levineuwirth.org`. No `~/universum` material enters
this repo; 04's, 07's and 08's content is textbook cops-and-robber
(Nowakowski–Winkler, Quilliot, Berarducci–Intrigila, Aigner–Fromme,
Schröder, Frankl for Meyniel) for that reason, and 08's five DOIs
(Quilliot's thesis has none) were checked against doi.org and Crossref
before they were set.

## Open questions

- Track this file, or gitignore it as the Forgejo notes are? It is written
  to be tracked, and has been, eight times.
