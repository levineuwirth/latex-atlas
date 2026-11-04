#!/usr/bin/env python3
"""Render the six starter patterns after ./build-beamer.sh --starter."""
from preview_grand import render_gallery


if __name__ == '__main__':
    render_gallery('atlas-starter', 'starter', [
        ('01-opening', 'One idea, clearly seen'),
        ('02-content', 'Make one comparison worth remembering', 2, 2),
        ('03-figure', 'The full comparison'),
        ('04-detail', 'The last pair makes the difference visible'),
        ('05-quotation', 'Give the evidence room.'),
        ('06-closing', 'Make the comparison count.'),
    ])
