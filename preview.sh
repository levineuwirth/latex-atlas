#!/bin/sh
# SPDX-License-Identifier: CC-BY-SA-4.0
# Render the first page of each built PDF to PNG at 100 dpi with poppler's
# pdftoppm: full plates into preview/, lab variants into preview/ablate/.
# Run ./build.sh --ablate first. Output is byte-reproducible for an
# unchanged PDF, so a clean rebuild leaves the working tree clean.
#
#   ./preview.sh [name ...]
set -u
mkdir -p preview preview/ablate
for pdf in build/*.pdf; do
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
