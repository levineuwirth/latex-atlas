#!/usr/bin/env python3
"""Render nine plates after ./build-beamer.sh --crawler."""
from preview_grand import render_gallery


if __name__ == '__main__':
    render_gallery('crawler-chronicles', 'crawler', [
        ('01-cover', 'Dispatches from a small public forge'),
        ('02-volume', 'Three days of enthusiastic readership'),
        ('03-anubis', 'Enter Anubis.'),
        ('04-repositories', 'the original repository-traffic figure'),
        ('05-publication', 'A commit’s birthday is not its public debut', 2, 2),
        ('06-comparison', 'The apparent bump meets its comparison'),
        ('07-versions', 'The swarm was chiefly revisiting the past'),
        ('08-court', 'The Court of Unnecessary Computation convenes'),
        ('09-finis', 'The finding entered into the record'),
    ])
