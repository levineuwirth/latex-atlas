#!/bin/sh
# SPDX-License-Identifier: CC-BY-SA-4.0
# Build the Atlas specimen. Outputs and logs stay in build/beamer/.
set -eu

plain=0
handout=0
grand=0
euler=0
crawler=0
for arg in "$@"; do
  case "$arg" in
    --plain) plain=1 ;;
    --handout) handout=1 ;;
    --grand) grand=1 ;;
    --euler) euler=1 ;;
    --crawler) crawler=1 ;;
    -h|--help) echo 'Usage: ./build-beamer.sh [--grand | --euler | --crawler] [--plain] [--handout]'; exit 0 ;;
    *) echo "build-beamer.sh: unknown option $arg" >&2; exit 2 ;;
  esac
done
if [ "$((grand + euler + crawler))" -gt 1 ]; then
  echo 'build-beamer.sh: choose one of --grand, --euler, or --crawler' >&2
  exit 2
fi

cd "$(dirname "$0")"
export TEXINPUTS="$(pwd)/sty:${TEXINPUTS-}:"
mkdir -p build/beamer
job=atlas
source=presentations/atlas.tex
theme=beamerthemeAtlas
passes=2
setup=''
if [ "$grand" -eq 1 ]; then
  job=atlas-grand
  source=presentations/atlas-grand.tex
  theme=beamerthemeAtlasGrand
  passes=3
fi
if [ "$euler" -eq 1 ]; then
  job=atlas-euler
  source=presentations/atlas-euler.tex
  theme=beamerthemeAtlasGrand
  passes=3
fi
if [ "$crawler" -eq 1 ]; then
  job=crawler-chronicles
  source=presentations/crawler-chronicles.tex
  theme=beamerthemeAtlasGrand
  passes=3
fi
if [ "$plain" -eq 1 ]; then
  job="$job-plain"
  setup="$setup\PassOptionsToPackage{plain}{$theme}"
fi
if [ "$handout" -eq 1 ]; then
  job="$job-handout"
  setup="$setup\PassOptionsToClass{handout}{beamer}"
fi
log="build/beamer/$job.stdout.txt"
: > "$log"
pass=1
while [ "$pass" -le "$passes" ]; do
  if ! lualatex -interaction=nonstopmode -halt-on-error \
    -output-directory=build/beamer -jobname="$job" \
    "$setup\input{$source}" >> "$log" 2>&1; then
    tail -30 "$log" >&2
    exit 1
  fi
  pass=$((pass + 1))
done
echo "Built build/beamer/$job.pdf"
