# SPDX-License-Identifier: CC-BY-SA-4.0
"""Check frozen essay sources without access to the author's website checkout."""
import hashlib
import json
from pathlib import Path
import unittest


class FrozenAssetsTests(unittest.TestCase):
    def test_originals_match_the_recorded_hashes(self):
        assets = Path(__file__).resolve().parent.parent / 'presentations/crawler-assets'
        files = json.loads((assets / 'manifest.json').read_text())['files']
        self.assertTrue(files, 'The source manifest must not be empty')
        self.assertEqual(set(files), {p.name for p in (assets / 'originals').iterdir()})
        for name, record in files.items():
            with self.subTest(asset=name):
                data = (assets / 'originals' / name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'])


if __name__ == '__main__':
    unittest.main()
