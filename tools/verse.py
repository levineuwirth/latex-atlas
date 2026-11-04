#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Plain text to atlas-verse LaTeX.

    tools/verse.py poems.txt > poems.tex            the poems only
    tools/verse.py --book "The Title" --author "A. B." --date "2026" poems.txt
                                                   a complete book, ready for
                                                   the recipe in README

The text file:

    # Title              a poem begins; its title
    #* Title             a poem whose lines are centred (shaped verse)
    lines                every non-blank line is a verse line
                         a blank line separates stanzas
        indented         leading spaces (or a tab) indent the line: \\vin
                         per four spaces
    @ text               after the poem: its attribution (a date, a place)
    % text               a comment, dropped
    ---                  a tailpiece after the poem (else none)

LaTeX's special characters are escaped (& % $ # _ { } ~ ^ \\); everything
else -- curly quotes, dashes, accents -- goes through as typed, since the
faces are Unicode. The poems' first lines and widths are measured by the
style itself, so nothing here needs to know a line's length.

Run it on a copy of the poems, and keep the output beside them, not in
latex-atlas: nothing of a poem enters that repository.
"""
import argparse
import string
import sys

SPECIALS = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}
TAB = 4


def escape(s):
    return "".join(SPECIALS.get(c, c) for c in s)


def indent_of(line):
    n = 0
    for c in line:
        if c == " ":
            n += 1
        elif c == "\t":
            n += TAB
        else:
            break
    return n // TAB


def convert(text):
    out = []
    in_poem = False
    centred = False
    pending_blank = False
    first_line = True

    def close():
        nonlocal in_poem
        if in_poem:
            out.append("\\end{poem*}" if centred else "\\end{poem}")
            in_poem = False

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("%"):
            continue
        if line.startswith("#"):
            close()
            centred = line.startswith("#*")
            title = line.lstrip("#*").strip()
            out.append("")
            out.append(f"\\poemtitle{{{escape(title)}}}")
            out.append("\\begin{poem*}" if centred else "\\begin{poem}")
            in_poem = True
            pending_blank = False
            first_line = True
            continue
        if line.strip() == "---":
            close()
            out.append("\\tailpiece")
            continue
        if line.startswith("@"):
            close()
            out.append(f"\\attribution{{{escape(line[1:].strip())}}}")
            continue
        if not line.strip():
            if in_poem and not first_line:
                pending_blank = True
            continue
        if not in_poem:
            # prose between poems, passed through as a paragraph
            out.append(escape(line))
            continue
        if pending_blank:
            out.append("")
            pending_blank = False
        vin = "\\vin " * indent_of(raw)
        out.append(f"{vin}{escape(line.strip())}\\\\")
        first_line = False
    close()
    return "\n".join(out).strip() + "\n"


HEADER = string.Template(r"""%!TEX program = lualatex
% Made by latex-atlas/tools/verse.py. Build, three times:
%   TEXINPUTS=~/Repos/personal/latex-atlas/sty: lualatex \
%     "\def\atlasrevision{...}\def\atlassetdate{...}\input{$name}"
\documentclass[11pt]{article}
\usepackage{atlas-grand}          % or {atlas} for the quiet edition
\usepackage{atlas-verse}
\AtlasPoemsOnNewPages             % or not, if the poems should flow
\title{$title}
\author{$author}
\date{$date}
\providecommand{\atlassources}{the author's manuscript}
\AtEndDocument{\AtlasFirstLines\AtlasColophon}

\begin{document}
\maketitle

""")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="the plain-text poems ('-' for stdin)")
    ap.add_argument("--book", metavar="TITLE", help="emit a complete book with this title")
    ap.add_argument("--author", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--name", default="book.tex", help="the .tex file's name, for the header's comment")
    a = ap.parse_args()
    text = sys.stdin.read() if a.source == "-" else open(a.source, encoding="utf-8").read()
    body = convert(text)
    if a.book:
        sys.stdout.write(HEADER.substitute(title=escape(a.book), author=escape(a.author),
                                           date=escape(a.date), name=a.name))
        sys.stdout.write(body)
        sys.stdout.write("\n\\end{document}\n")
    else:
        sys.stdout.write(body)


if __name__ == "__main__":
    main()
