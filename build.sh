#!/bin/sh
# SPDX-License-Identifier: CC-BY-SA-4.0
# Compile every example into build/. Run from the repository root.
# Usage: ./build.sh [example-name ...]
set -u
mkdir -p build
failed=""
for file in examples/*.tex; do
  [ -e "$file" ] || continue
  name=$(basename "${file%.*}")
  if [ "$#" -gt 0 ]; then
    case " $* " in *" $name "*) ;; *) continue ;; esac
  fi
  lualatex -interaction=nonstopmode -halt-on-error -output-directory=build "$file" > "build/$name.stdout.txt" 2>&1
  if [ $? -eq 0 ]; then echo "OK   $name"; else echo "FAIL $name"; failed="$failed $name"; fi
done
if [ -n "$failed" ]; then echo "Failed:$failed" >&2; exit 1; fi
