#!/bin/sh
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
# Rewrite the lab gallery in README.md, between the "<!-- lab:begin -->" and
# "<!-- lab:end -->" markers, from the controls found in examples/*.tex and
# the PNGs preview.sh renders. Four plates per row: the full treatment, then
# one cell per control with that control at its modern default, then plain.
set -u
tmp=$(mktemp) || exit 1
{
  echo '<!-- lab:begin -->'
  for file in examples/*.tex; do
    [ -e "$file" ] || continue
    name=$(basename "${file%.*}")
    title=$(echo "$name" | sed 's/-/ /g')
    cells="full|preview/$name.png|examples/$name.tex"
    for ctl in $(grep -o '\\atlascontrol{[a-z0-9-]*}' "$file" | sed 's/.*{\(.*\)}/\1/' | awk '!seen[$0]++'); do
      cells="$cells
without $ctl|preview/ablate/$name--no-$ctl.png|"
    done
    cells="$cells
plain|preview/ablate/$name--plain.png|"
    echo
    echo "### $title"
    echo
    echo "$cells" | awk -F'|' '
      { n++; lab[n]=$1; img[n]=$2; src[n]=$3 }
      END {
        for (i = 1; i <= n; i += 4) {
          last = (i + 3 < n) ? i + 3 : n
          print "| | | | |"
          print "|:-:|:-:|:-:|:-:|"
          row = "|"
          for (j = i; j <= last; j++) {
            cell = "![" lab[j] "](" img[j] ")"
            if (src[j] != "") cell = "[" cell "](" src[j] ")"
            row = row " " cell " |"
          }
          for (j = last + 1; j <= i + 3; j++) row = row " |"
          print row
          row = "|"
          for (j = i; j <= last; j++) row = row " " lab[j] " |"
          for (j = last + 1; j <= i + 3; j++) row = row " |"
          print row
          if (last < n) print ""
        }
      }'
  done
  echo
  echo '<!-- lab:end -->'
} > "$tmp"
awk -v gen="$tmp" '
  /<!-- lab:begin -->/ { while ((getline line < gen) > 0) print line; skip = 1; next }
  /<!-- lab:end -->/   { skip = 0; next }
  !skip { print }
' README.md > "$tmp.readme" && mv "$tmp.readme" README.md
rm -f "$tmp"
echo "README.md lab gallery regenerated"
