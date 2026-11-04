#!/bin/sh
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
# Render the first page of each built plate to PNG at 100 dpi with poppler's
# pdftoppm: full plates into preview/, lab variants into preview/ablate/.
# Run ./build.sh --ablate first. Output is byte-reproducible for an
# unchanged PDF, so a clean rebuild leaves the working tree clean.
#
# Only plates -- build/NN-*.pdf -- are rendered. build/ also holds dressed
# manuscripts (see README, "The style"), and nothing of those may reach
# preview/, which is committed.
#
#   ./preview.sh [name ...]
set -u
mkdir -p preview preview/ablate
for pdf in build/[0-9][0-9]-*.pdf; do
  [ -e "$pdf" ] || continue
  name=$(basename "${pdf%.pdf}")
  if [ "$#" -gt 0 ]; then
    case " $* " in *" $name "*) ;; *) continue ;; esac
  fi
  pdftoppm -png -r 100 -singlefile "$pdf" "preview/$name" && echo "preview/$name.png"
  for v in build/ablate/"$name"--*.pdf; do
    [ -e "$v" ] || continue
    vname=$(basename "${v%.pdf}")
    pdftoppm -png -r 100 -singlefile "$v" "preview/ablate/$vname" \
      && echo "preview/ablate/$vname.png"
  done
done
