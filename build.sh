#!/bin/sh
# SPDX-License-Identifier: CC-BY-SA-4.0
# Compile examples into build/. Run from the repository root.
#
#   ./build.sh                         every example, full treatment
#   ./build.sh 01-rubricated-incipit   a subset, by name
#   ./build.sh --ablate [name ...]     also the lab variants of each example:
#                                      one per control with that control set
#                                      to its modern default, and one with
#                                      all of them (--plain), in build/ablate/
#   ./build.sh -j4 --ablate            four jobs at once (-j 4 too); bare -j
#                                      means nproc.
#                                      Sequential by default, so the report
#                                      comes out in a stable order.
#
# A control is an \atlascontrol{<name>}{...}{...} call in the example; the
# names to omit reach the document as \atlasomit on the lualatex command
# line, so no file is edited to produce a variant.
#
# One lualatex run is the rule. A plate that needs more says so in its
# header, next to %!TEX program, and the declaration is found by grep
# exactly as the controls are:
#
#   %!ATLAS passes=2                   run lualatex twice (default 1)
#   %!ATLAS biber                      run biber after the first pass
#
# Every variant inherits both: -jobname keeps each variant's .aux, .bcf and
# .bbl apart, so nothing else changes. The passes append to <job>.stdout.txt
# in the output directory; biber writes <job>.biber.txt beside its .blg.
# The steps run in order and stop at the first failure.
set -u

controls_of() {
  grep -o '\\atlascontrol{[a-z0-9-]*}' "$1" | sed 's/.*{\(.*\)}/\1/' | awk '!seen[$0]++'
}

passes_of() {
  n=$(grep -m1 -o '^%!ATLAS passes=[0-9][0-9]*' "$1" | sed 's/.*=//')
  echo "${n:-1}"
}

wants_biber() {
  grep -q '^%!ATLAS biber *$' "$1"
}

# compile <file> <jobname> <outdir> <omit-list>
compile() {
  passes=$(passes_of "$1")
  : > "$3/$2.stdout.txt"
  pass=1
  while [ "$pass" -le "$passes" ]; do
    lualatex -interaction=nonstopmode -halt-on-error \
      -output-directory="$3" -jobname="$2" \
      "\\def\\atlasomit{$4}\\input{$1}" >> "$3/$2.stdout.txt" 2>&1 || return 1
    if [ "$pass" -eq 1 ] && wants_biber "$1"; then
      biber --input-directory "$3" --output-directory "$3" "$2" \
        > "$3/$2.biber.txt" 2>&1 || return 1
    fi
    pass=$((pass + 1))
  done
}

# one <file>|<jobname>|<outdir>|<omit-list>: compile a job and report it on
# one line. This is what xargs runs, one process per job; POSIX sh cannot
# export a function, so the script re-enters itself with --one.
one() {
  file=${1%%|*}; rest=${1#*|}
  job=${rest%%|*}; rest=${rest#*|}
  outdir=${rest%%|*}; omit=${rest#*|}
  if compile "$file" "$job" "$outdir" "$omit"; then echo "OK   $job"; else echo "FAIL $job"; return 1; fi
}

# jobs_of [name ...]: the job list, one <file>|<jobname>|<outdir>|<omit-list>
# line per PDF to build, in the order the report should read.
jobs_of() {
  for file in examples/*.tex; do
    [ -e "$file" ] || continue
    name=$(basename "${file%.*}")
    if [ "$#" -gt 0 ]; then
      case " $* " in *" $name "*) ;; *) continue ;; esac
    fi
    echo "$file|$name|build|"
    [ "$ablate" -eq 1 ] || continue
    all=""
    for ctl in $(controls_of "$file"); do
      all="${all:+$all,}$ctl"
      echo "$file|$name--no-$ctl|build/ablate|$ctl"
    done
    if [ -n "$all" ]; then echo "$file|$name--plain|build/ablate|$all"; fi
  done
}

# Options and plate names may be mixed in any order; an unknown option is
# an error rather than a silently ignored name.
ablate=0
jobs=1
names=""
while [ "$#" -gt 0 ]; do
  case $1 in
    --ablate) ablate=1 ;;
    -j) case ${2-} in ''|*[!0-9]*) jobs=$(nproc) ;; *) jobs=$2; shift ;; esac ;;
    -j[0-9]*) jobs=${1#-j} ;;
    --one) [ -n "${2-}" ] || exit 0; one "$2"; exit ;;
    -*) echo "build.sh: unknown option $1" >&2; exit 2 ;;
    *) names="$names $1" ;;
  esac
  shift
done

mkdir -p build build/ablate
tmp=$(mktemp) || exit 1
trap 'rm -f "$tmp" "$tmp.jobs"' EXIT
# shellcheck disable=SC2086  # names is a space-separated list on purpose
jobs_of $names > "$tmp.jobs"
if [ ! -s "$tmp.jobs" ]; then
  echo "build.sh: no plate matches:$names" >&2
  exit 1
fi
xargs -P "$jobs" -L1 sh "$0" --one < "$tmp.jobs" | tee "$tmp"
if grep -q '^FAIL' "$tmp"; then
  echo "Failed:$(grep '^FAIL' "$tmp" | sed 's/^FAIL//' | tr -d '\n')" >&2
  exit 1
fi
