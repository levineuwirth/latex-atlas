<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 the repository contributors -->

# Releases

[Back to Atlas](../README.md) · [0.1.0 release notes](../release/NOTES.md)

The release archive is a selected, self-contained copy of the CLI, both
Beamer themes, starter, reusable helpers, and Atlas/Grand/Euler sources.
It includes three fresh sample PDFs: Grand, Euler, and the starter handout.
The license texts and notices travel with the files. Crawler assets,
the article/verse lab, Git history, local logs, and font binaries are not
included.

## Build and verify a candidate

From a clean checkout, with the README dependencies installed:

```sh
python3 tools/release.py
```

The version comes from `VERSION`. The command compiles and checks the
sample PDFs, creates `build/release/latex-atlas-0.1.0.tar.gz`, extracts it
outside the checkout, and exercises the shipped CLI there. It creates a
new talk, builds all four variants, generates a preview, and verifies
that the TeX dependencies came from the extracted themes. The final
validation report and `SHA256SUMS` are beside the archive. A failed test
returns nonzero; an archive alone does not indicate a verified candidate.

The archive's `MANIFEST.json` records the source commit, version, and each
file's SHA-256. Packaging normalizes timestamps and file modes; identical
input files produce identical archives. PDF generation can still differ
between TeX/font versions, so the manifest also records the compiler version.

For development only, `--allow-dirty` permits uncommitted changes and marks
the manifest accordingly. Public releases should be built from a clean
commit. `--output-dir` chooses a different artifact directory.

CI runs the same packaging and extraction check and saves the release
candidate as a workflow artifact. To verify a downloaded release:

```sh
sha256sum -c SHA256SUMS
tar -xzf latex-atlas-0.1.0.tar.gz
cd latex-atlas-0.1.0
./atlas --version
```

Download the three sample PDFs beside the archive if checking the complete
`SHA256SUMS` file; they are also inside the archive under `samples/`.

## Publishing

Prepare and review the candidate before changing repository visibility.
Create a draft GitHub release for `v0.1.0` at the manifest's exact commit,
attach the archive, `SHA256SUMS`, and sample PDFs, and use
`release/NOTES.md` as the description. Review the draft, CI result, and
downloaded bundle before publishing. Repository visibility and release
publication are separate actions; the builder performs neither.
