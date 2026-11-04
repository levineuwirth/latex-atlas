# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the repository contributors
"""Fast archive checks; real builds and extraction are exercised by release.py."""
import json
from pathlib import Path
import tempfile
import unittest

import release


class ReleaseTests(unittest.TestCase):
    def test_allowlist_has_runtime_and_notices_without_restricted_assets(self):
        self.assertTrue({'atlas', 'VERSION', 'tools/atlas_cli.py',
                         'presentations/starter.tex', 'LICENSE', 'LICENSE-CONTENT',
                         'NOTICES', 'presentations/LICENSE', 'samples/LICENSE'} <= set(release.FILES))
        for destination, source in release.FILES.items():
            with self.subTest(path=source):
                self.assertTrue((release.ROOT / source).is_file())
                self.assertNotIn('crawler', destination)
                self.assertNotIn('crawler', source)
                self.assertFalse(source.startswith(('build/', '.git/', 'bound/', 'examples/')))

    def test_archive_is_repeatable_and_detects_changed_contents(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / 'latex-atlas-0.1.0'
            bundle.mkdir()
            (bundle / 'atlas').write_text('executable')
            (bundle / 'LICENSE').write_text('notice')
            manifest = release.make_manifest(bundle, '0.1.0', 'test-commit', False, 'test compiler')
            (bundle / 'MANIFEST.json').write_text(json.dumps(manifest))
            first, second = root / 'one.tar.gz', root / 'two.tar.gz'
            release.write_archive(bundle, first, 1000)
            (bundle / 'atlas').touch()  # filesystem timestamps must not affect the archive
            release.write_archive(bundle, second, 1000)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            extracted = release.unpack_and_verify(first, root / 'out', bundle.name)
            self.assertEqual((extracted / 'atlas').stat().st_mode & 0o777, 0o755)
            self.assertEqual((extracted / 'LICENSE').read_text(), 'notice')
            (bundle / 'LICENSE').write_text('changed without updating manifest')
            release.write_archive(bundle, second, 1000)
            with self.assertRaisesRegex(ValueError, 'Checksum mismatch: LICENSE'):
                release.unpack_and_verify(second, root / 'bad', bundle.name)


if __name__ == '__main__':
    unittest.main()
