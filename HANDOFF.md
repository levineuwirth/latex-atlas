# latex-atlas — handoff

Written 2026-09-15 at the end of the session that turned the examples
into a lab. Read the README first; this file is what the README does not
say: why things are the way they are, what the lab has shown so far, what
bit us, and what to do next.

---

## Where it stands

`main` at `8171c63`, pushed to `ssh://git@git.levineuwirth.org:2222/neuwirth/latex-atlas.git`.
Tree clean. Six plates, 43 PDFs from `./build.sh --ablate` in ~35 s, every
preview byte-reproducible from a clean build *on this machine* (see the
font caveat below).

| plate | register | controls |
|---|---|---|
| 01 rubricated incipit | functional | paper, rubric, pilcrow, initial, runhead |
| 02 marginal scholia | functional | paper, margin, gloss, catchword, folio |
| 03 hatched bar chart | functional | paper, hatch, table, lining |
| 04 propositions | functional | mathfont, paper, heads, qed, scholium |
| 05 engraved graph plate | both | paper, taper, matching, stipple, frame, lettering |
| 06 hand-press impression | costume | paper, jitter, inkspread, inking, laid, foxing |

Commits so far: `69a8fec` initial three plates; `01858bd` tint notes;
`60f0dc2` the lab plus retrofits; `8171c63` plates 04–06.

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
   matched math font. Never an empty page or a hole. A control whose
   ablation is "nothing" (frame, catchword, laid, foxing) is fine only
   when nothing *is* the modern default.

## What the ablations have shown

Look at `preview/ablate/` before building more; these are the findings.

- **The gloss needs the margin** (`02 --no-margin`): at a 20 mm margin
  column the note survives but chokes and overflows below the text. The
  device and the page geometry are one decision, which matters for the
  `.sty`.
- **Hatch vs grey** (`03 --no-hatch`) is the cleanest single argument in
  the repo: same data, same layout, one of them photocopies.
- **The engraved lens needs heavier figures than a uniform line.** A
  lens averages far thinner than its widest point; the taper control
  uses 0.9 pt / 2.2 pt half-widths where the uniform fallback takes
  0.6 × the same figure. First attempt at 0.5 pt looked like pencil.
- **Pagella Math beside Pagella is invisible in the right way**
  (`04 --no-mathfont` shows the Latin Modern mismatch). Garamond-Math
  beside EB Garamond is untested here (fonts absent, below).
- **Paper tint** ablates cleanly everywhere and every plate looks fine on
  white. The six tints are within a few units of each other; when the
  `.sty` comes, one token will do.
- **Jitter at 0.28 pt, squash 0.09 ± 0.07 pt** (06) is the tuned point:
  visible at 300 dpi, not a bold face. 0.35 / 0.16 read as a bold weight.

## Re-read before touching the plates

Things that cost time once and should not cost it twice.

- **Control names are found by grep** (`\atlascontrol{[a-z0-9-]*}`),
  so never write `\atlascontrol{word}` in a comment — the README-style
  `\atlascontrol{<name>}` with angle brackets is safe. Names are
  lower-case letters, digits, hyphens.
- **The lab block is inlined in every plate, identically.** That is the
  price of standalone files. If it changes, change it in all six.
- **`\newcommand{\foo}[1]{#1}` inside a control argument works** — `#`
  survives xparse's `+m` grabbing. Verified.
- **`even odd rule` is a scoped option and TikZ forbids options on a
  clip path.** Put it on the scope: `\begin{scope}[even odd rule] \clip …`.
- **Don't use `remember picture`/`current page`** — it needs two runs and
  `build.sh` does one. Draw page furniture in
  `\AddToHook{shipout/background}{\put(0,0){…}}`: origin top-left, y
  negative downward, `(\paperwidth,-\paperheight)` is the far corner.
- **Lua goes in `luacode*`, not `\directlua`**, so `%`, `#` and `--`
  comments are safe. Controls then only poke numbers:
  `\atlascontrol{jitter}{\directlua{atlas.jitter = 0.28}}{}`.
- **The ink squash is a `pdf_literal` whatsit, `mode = 1`, `2 Tr w`, with
  a `0 Tr` appended at the end of the line** so headers, footers and the
  next paragraph don't inherit the stroke. Confirmed in the stream with
  `qpdf --qdf`.
- **Fonts: EB Garamond and Garamond-Math were installed at the end of the
  session** (`texlive-fontsextra`; luaotfload's database has been
  rebuilt). **The committed previews are still the Pagella renderings** —
  every plate selects EB Garamond via `\IfFontExistsTF`, so the next
  `./build.sh --ablate && ./preview.sh` regenerates all 43 PNGs in the
  new face. That is the first thing to do: look at 04 in particular
  (Garamond-Math with `StylisticSet={5,7}` is untested), retune anything
  the change of face upsets (measure, lettrine size, 06's amplitudes), and
  commit the regenerated previews as one commit. Pagella stays as the
  fallback for machines without the fonts.
- **`preview/` is 5.5 MB** (37 ablations at 100 dpi). Kept full-size so
  clicking through is worth it. If the repo grows past ~15 plates, drop
  the ablations to 60 dpi in `preview.sh` (one number) and regenerate.
- **`vintage-latex` lives in `~/scratch/tmp/vintage-latex`**, a scratch
  directory, and the README points there. If it matters — 20 plates and
  the fiziko work — move it under `~/Repos` before it gets swept.

## Outstanding, in rough order

Ideas raised and agreed worth trying; none started. The first two feed
the preprint style directly, the rest are lab material.

1. **Front matter** — "The Argument" as abstract, a *Table of the
   Propositions* as theorem index, title block. Functional; pairs with 04.
2. **Bibliography** — a period reference list in biblatex: hanging entries,
   small-caps authors, old-style years, no naked URLs. Functional; the
   `.sty` cannot ship without it.
3. **Colophon and errata slip** — fonts/engine/date/git hash (needs
   `--shell-escape` or a build-time `\def`; decide which), and an errata
   slip as revision notes. Rhymes with the site's colophon page.
4. **Fold-out plate** — a landscape leaf for a wide table, "Plate II, to
   face p. 12". Period convention with a modern use.
5. **Marginal figures** — small graph drawings in the scholia margin, the
   natural sequel to 02 + 05 for a graph-theory paper.
6. **Screen vs print edition** from one source (parchment on a display,
   white for print/arXiv). Probably the first real `.sty` option.
7. **The `.sty` graduation** itself — `\usepackage[rubric,scholia,plain]{atlas}`
   or similar. Only once 1–2 exist; the tokens that survive ablation
   across plates (paper, ink, rubric) become the package's tokens.
8. **CSS counterparts for the Hakyll site** so an HTML preprint matches
   its PDF. Separate repo when it happens.

The site export path is unchanged: sources in `~/Repos/research/meyniel`,
`make export` to `levineuwirth.org`. No `~/universum` material enters
this repo; 04's content is textbook cops-and-robber (Nowakowski–Winkler,
Berarducci–Intrigila, Meyniel's conjecture) for that reason.

## Open questions

- Track this file, or gitignore it as the Forgejo notes are? It is written
  to be tracked.
- Does the `.sty` want the lab controls too (so a preprint can be ablated),
  or is that lab-only machinery?
