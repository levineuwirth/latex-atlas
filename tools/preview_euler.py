#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Render the Euler gallery after ./build-beamer.sh --euler."""
from preview_grand import render_gallery


if __name__ == '__main__':
    render_gallery('atlas-euler', 'euler', [
        ('01-cover', 'A geometry of what remains'),
        ('02-net', 'Let the surface open', 3, 3),
        ('03-plane', 'Give one face to the horizon', 2, 2),
        ('04-erasure', 'One boundary less; one region less', 6, 4),
        ('05-tree', 'Nothing is enclosed.'),
        ('06-point', 'The irreducible drawing'),
        ('07-formula', "Euler’s polyhedral formula"),
        ('08-solids', 'Many forms; the same remainder'),
        ('09-theorem', 'The shape of the theorem'),
    ])
