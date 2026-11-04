#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Audit the actual diagram's edge lists using geometric face walks.

This counts faces independently of Euler's formula. Each erasure must
merge two distinct faces; each pruning step must remove a leaf. It also
checks the rigid-face geometry used for the unfolding plates.
"""
from math import atan2
from pathlib import Path
import re
from euler_geometry import validate


def faces(vertices, edges):
    if not edges:
        assert len(vertices) == 1
        return [set()]
    neighbors = {v: [] for v in vertices}
    for a, b in edges:
        neighbors[a].append(b)
        neighbors[b].append(a)
    for v, ns in neighbors.items():
        x, y = vertices[v]
        ns.sort(key=lambda n: atan2(vertices[n][1]-y, vertices[n][0]-x))
    seen, result = set(), []
    for a, b in [(a, b) for a, ns in neighbors.items() for b in ns]:
        if (a, b) in seen:
            continue
        boundary, u, v = set(), a, b
        while (u, v) not in seen:
            seen.add((u, v))
            boundary.add((u, v))
            ns = neighbors[v]
            u, v = v, ns[(ns.index(u)-1) % len(ns)]
        assert (u, v) == (a, b)
        result.append(boundary)
    return result


def connected(vertices, edges):
    seen = {next(iter(vertices))}
    while True:
        new = {v for a, b in edges if a in seen or b in seen for v in (a, b)}
        if new <= seen:
            return len(seen) == len(vertices)
        seen |= new


def main():
    root = Path(__file__).resolve().parent.parent
    text = (root/'presentations/euler-plates.tex').read_text()
    body = text.split(r'\newcommand{\EulerMap}')[1].split(r'\newcommand{\EulerLedger}')[0]
    vertex_data = re.search(r'\\foreach \\name/\\x/\\y in \{([^}]+)\}', body)[1]
    vertices = {n: (float(x), float(y)) for n, x, y in
                (row.split('/') for row in vertex_data.split(','))}
    lists = re.findall(r'\\foreach \\u/\\v/\\step in \{([^}]+)\}', body)
    assert len(lists) == 2
    removed, tree = [[(a, b) for a, b, _ in (row.split('/') for row in data.split(','))]
                     for data in lists]
    edges = removed+tree
    assert len(vertices) == 8 and len(edges) == 12
    for i in range(6):
        regions = faces(vertices, edges)
        assert connected(vertices, edges)
        assert len(regions) == 6-i
        assert len(vertices)-len(edges)+len(regions) == 2
        if i < 5:
            a, b = removed[i]
            assert next(j for j, f in enumerate(regions) if (a, b) in f) != next(
                j for j, f in enumerate(regions) if (b, a) in f)
            edges.remove((a, b))
    for a, b in tree:
        assert sum(a in e for e in edges) == 1
        edges.remove((a, b))
        del vertices[a]
        assert connected(vertices, edges)
        assert len(faces(vertices, edges)) == 1
        assert len(vertices)-len(edges)+1 == 2
    assert set(vertices) == {'e'} and not edges
    cube = text.split(r'\newcommand{\EulerCube}')[1].split(r'\newcommand{\EulerSphere}')[0]
    bounds = re.search(r'bounding box\] \(([^,]+),([^\)]+)\) rectangle \(([^,]+),([^\)]+)\)', cube)
    left, bottom, right, top = map(float, bounds.groups())
    rows = re.search(r'\\foreach \\n/\\x/\\y in \{([^}]+)\}', cube)[1]
    for _, x, y in (row.split('/') for row in rows.split(',')):
        x, y = float(x), float(y)
        # Include the vertex highlight rings, not just vertex centers.
        assert left < x-.14 and x+.14 < right and bottom < y-.14 and y+.14 < top
    validate()
    print('Passed: six cycle-erasure states, seven leaf removals, rigid cube hinges, and camera bounds.')


if __name__ == '__main__':
    main()
