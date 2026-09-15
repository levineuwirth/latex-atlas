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
#
# A control is an \atlascontrol{<name>}{...}{...} call in the example; the
# names to omit reach the document as \atlasomit on the lualatex command
# line, so no file is edited to produce a variant.
set -u
ablate=0
if [ "${1-}" = "--ablate" ]; then ablate=1; shift; fi
mkdir -p build build/ablate
failed=""

controls_of() {
  grep -o '\\atlascontrol{[a-z0-9-]*}' "$1" | sed 's/.*{\(.*\)}/\1/' | awk '!seen[$0]++'
}

# compile <file> <jobname> <outdir> <omit-list>
compile() {
  lualatex -interaction=nonstopmode -halt-on-error \
    -output-directory="$3" -jobname="$2" \
    "\\def\\atlasomit{$4}\\input{$1}" > "$3/$2.stdout.txt" 2>&1
}

report() {
  if [ "$1" -eq 0 ]; then echo "OK   $2"; else echo "FAIL $2"; failed="$failed $2"; fi
}

for file in examples/*.tex; do
  [ -e "$file" ] || continue
  name=$(basename "${file%.*}")
  if [ "$#" -gt 0 ]; then
    case " $* " in *" $name "*) ;; *) continue ;; esac
  fi
  compile "$file" "$name" build ""; report $? "$name"
  [ "$ablate" -eq 1 ] || continue
  all=""
  for ctl in $(controls_of "$file"); do
    all="${all:+$all,}$ctl"
    compile "$file" "$name--no-$ctl" build/ablate "$ctl"; report $? "$name--no-$ctl"
  done
  [ -n "$all" ] || continue
  compile "$file" "$name--plain" build/ablate "$all"; report $? "$name--plain"
done
if [ -n "$failed" ]; then echo "Failed:$failed" >&2; exit 1; fi
