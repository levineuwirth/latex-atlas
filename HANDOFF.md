# latex-atlas — handoff

Written 2026-09-15 at the end of the session that moved the previews to
EB Garamond and added the front matter. Read the README first; this file
is what the README does not say: why things are the way they are, what
the lab has shown so far, what bit us, and what to do next.

---

## Where it stands

`main` at `9e12c60`, remote
`ssh://git@git.levineuwirth.org:2222/neuwirth/latex-atlas.git`. Tree
clean. Seven plates, 51 PDFs from `./build.sh --ablate` in ~50 s, every
preview byte-reproducible from a clean build (verified this session:
`rm -rf build && ./build.sh --ablate && ./preview.sh` left the tree clean).

| plate | register | controls |
|---|---|---|
| 01 rubricated incipit | functional | paper, rubric, pilcrow, initial, runhead |
| 02 marginal scholia | functional | paper, margin, gloss, catchword, folio |
| 03 hatched bar chart | functional | paper, hatch, table, lining |
| 04 propositions | functional | mathfont, paper, heads, qed, scholium |
| 05 engraved graph plate | both | paper, taper, matching, stipple, frame, lettering |
| 06 hand-press impression | costume | paper, jitter, inkspread, inking, laid, foxing |
| 07 front matter | both | paper, imprint, title, argument, table, fleuron |

Commits so far: `69a8fec` initial three plates; `01858bd` tint notes;
`60f0dc2` the lab plus retrofits; `8171c63` plates 04–06; `af94c05` first
handoff; `c5a3983` previews in EB Garamond and the retunes; `9e12c60`
plate 07.

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
  04–07 (03 never asked for them): "connected", "demonstration",
  "strike". Deliberate and kept — it is the period's face — but note
  that a preprint `.sty` in the functional register may want `Rare`
  off; that is a `.sty` decision, not a plate one.

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
- **`preview/` is ~6 MB** (45 ablations at 100 dpi). Kept full-size so
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
  invented; the treatise is not on the page.
- The imprint says "to be had at levineuwirth.org" — the period's "to be
  sold by", with the site standing in for the bookseller. It is the only
  URL in the repo and it is set as text, not a link.
- `\tableline` takes both a period head and a modern one
  (`{Scholium.}{Remark}`) because the modern list would name amsthm's
  Remark, as 04's ablation does.

## Outstanding, in rough order

Ideas raised and agreed worth trying. The first feeds the preprint style
directly; the rest are lab material.

1. **Bibliography** — a period reference list in biblatex: hanging entries,
   small-caps authors, old-style years, no naked URLs. Functional; the
   `.sty` cannot ship without it. Note biblatex wants biber and a second
   run; either `build.sh` grows a two-pass mode for plates that declare
   it, or the plate hand-sets the entries as 07 hand-sets its page
   numbers. Decide before starting.
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
- Does `Ligatures=Rare` belong in the functional register at all? The
  lab can answer it: make it a control in 04 and look.
- Should `build.sh` learn a two-pass mode? Bibliography (1) and a real
  theorem index both want it. The one-run rule has been cheap so far.
