import hashlib
import unittest
from restore_legacy import verify, SOURCES


class LegacyRestorationTests(unittest.TestCase):
    def test_changed_dependency_rejected(self):
        expected = hashlib.sha256(b'original').hexdigest()
        verify(b'original', expected)
        with self.assertRaises(ValueError):
            verify(b'modified', expected)

    def test_only_audited_commits_enabled(self):
        self.assertEqual(set(SOURCES.values()), {'2.6.2', '2.8.2.1'})
        self.assertNotIn('972fdbfe9e40853afc09eb06f83045c95acfb53c', SOURCES)
