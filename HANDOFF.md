# latex-atlas — handoff

Written 2026-09-15 at the end of the session that moved the previews to
EB Garamond and added the front matter. Read the README first; this file
is what the README does not say: why things are the way they are, what
the lab has shown so far, what bit us, and what to do next.

---

## Where it stands

`main` at the commit that records the build.sh decision (after
`10debf3`, the review fixes), remote
`ssh://git@git.levineuwirth.org:2222/neuwirth/latex-atlas.git`. Tree
clean. Seven plates, 52 PDFs from `./build.sh --ablate` in ~50 s, every
preview byte-reproducible from a clean build (verified twice on
2026-09-15, once by the author's review session:
`rm -rf build && ./build.sh --ablate && ./preview.sh && ./gallery.sh`
left the tree clean).

| plate | register | controls |
|---|---|---|
| 01 rubricated incipit | functional | paper, rubric, pilcrow, initial, runhead |
| 02 marginal scholia | functional | paper, margin, gloss, catchword, folio |
| 03 hatched bar chart | functional | paper, hatch, table, lining |
| 04 propositions | functional | mathfont, paper, heads, qed, scholium |
| 05 engraved graph plate | both | paper, taper, matching, stipple, frame, lettering |
| 06 hand-press impression | costume | paper, jitter, inkspread, inking, laid, foxing |
| 07 front matter | both | ligatures, paper, imprint, title, argument, table, fleuron |

Commits so far: `69a8fec` initial three plates; `01858bd` tint notes;
`60f0dc2` the lab plus retrofits; `8171c63` plates 04–06; `af94c05` first
handoff; `c5a3983` previews in EB Garamond and the retunes; `9e12c60`
plate 07; `9aa387f` second handoff; then the review fixes (07's note
reconciled with 04, `ligatures` made a control in 07, this file).

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
  white. 07 takes 04's tint exactly, being the same book — the first
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

## Re-read before touching the plates

Things that cost time once and should not cost it twice.

- **Control names are found by grep** (`\atlascontrol{[a-z0-9-]*}`),
  so never write `\atlascontrol{word}` in a comment — the README-style
  `\atlascontrol{<name>}` with angle brackets is safe. Names are
  lower-case letters, digits, hyphens.
- **The lab block is inlined in every plate, identically.** That is the
  price of standalone files. If it changes, change it in all seven.
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
- **`preview/` is ~6 MB** (45 ablations at 100 dpi, 52 PNGs in all). Kept full-size so
  clicking through is worth it. If the repo grows past ~15 plates, drop
  the ablations to 60 dpi in `preview.sh` (one number) and regenerate.
- **`vintage-latex` lives in `~/scratch/tmp/vintage-latex`**, a scratch
  directory, and the README points there. If it matters — 20 plates and
  the fiziko work — move it under `~/Repos` before it gets swept.
- **Sweeping a parameter**: `sed` the value into copies of the plate in
  the scratch directory, compile each, crop with `pdftoppm -x -y -W -H`
  at 100 and 300 dpi, and `magick … -append` the crops into one stack.
  That is how 06's amplitudes were chosen; ten minutes, no guessing.

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

## Decided: build.sh grows passes, biber and -j

Decided 2026-09-15 between the author and the reviewing session, after
weighing (a) keeping one run and hand-setting the bibliography, (b) an
explicit per-plate opt-in, (c) latexmk for everything. **(b)**, because the
one-run rule has been information, not overhead — it caught
`remember picture` and `\today` — and should stay the default with every
exception declared in the file that needs it; and because the bibliography
plate's deliverable is a biblatex style for the `.sty`, which cannot be
developed hand-set. latexmk was rejected for hiding the pass count and
adding Perl for 45 variants that don't need it. Not yet implemented; this
is the spec.

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

## Outstanding, in rough order

Ideas raised and agreed worth trying. The first feeds the preprint style
directly; the rest are lab material.

0. **build.sh: passes, biber, -j** — implement the decided spec above.
   Small, and 1 depends on it. Prove it on 07 first (`passes=2`, no
   biber, output identical) before writing the plate that needs it.
1. **Bibliography (08)** — a period reference list in biblatex, the style
   written as a real `.bbx`/`.cbx` pair inside the plate (or a `.sty`-bound
   file once the graduation starts): hanging entries, small-caps authors,
   old-style years, no naked URLs, against `biblatex`'s `numeric` default.
   Candidate controls: hanging, authors (small caps vs plain), years
   (old-style vs lining), urls (DOI as text vs naked URL), and paper.
   Functional; the `.sty` cannot ship without it. Entries: the six
   attributions already on 04 and 07 (Nowakowski–Winkler, Quilliot,
   Berarducci–Intrigila, Aigner–Fromme, Schröder, Frankl for Meyniel), so
   the three plates cite one book.
2. **Colophon and errata slip** — fonts/engine/date/git hash (needs
   `--shell-escape` or a build-time `\def`; decide which), and an errata
   slip as revision notes. Rhymes with the site's colophon page and with
   07's imprint; keep the two distinct (imprint = title leaf, colophon =
   last leaf).
3. **Fold-out plate** — a landscape leaf for a wide table, "Plate II, to
   face p. 12". Period convention with a modern use.
4. **Marginal figures** — small graph drawings in the scholia margin, the
   natural sequel to 02 + 05 for a graph-theory paper.
5. **Screen vs print edition** from one source (parchment on a display,
   white for print/arXiv). Probably the first real `.sty` option.
6. **The `.sty` graduation** itself — `\usepackage[rubric,scholia,plain]{atlas}`
   or similar. 04 + 07 now give a complete treatise skeleton (front
   matter, apparatus); with 1 it could be tried. The tokens that survive
   ablation across plates (paper, ink, rubric) become the package's
   tokens.
7. **CSS counterparts for the Hakyll site** so an HTML preprint matches
   its PDF. Separate repo when it happens.

The site export path is unchanged: sources in `~/Repos/research/meyniel`,
`make export` to `levineuwirth.org`. No `~/universum` material enters
this repo; 04's and 07's content is textbook cops-and-robber
(Nowakowski–Winkler, Berarducci–Intrigila, Aigner–Fromme, Schröder,
Meyniel's conjecture) for that reason.

## Open questions

- Track this file, or gitignore it as the Forgejo notes are? It is written
  to be tracked, and has been, twice.
- Does the `.sty` want the lab controls too (so a preprint can be ablated),
  or is that lab-only machinery?
