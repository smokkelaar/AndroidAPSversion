import hashlib
import unittest
from unittest.mock import patch
from restore_legacy import verify, SOURCES, main


class LegacyRestorationTests(unittest.TestCase):
    def test_changed_dependency_rejected(self):
        expected = hashlib.sha256(b'original').hexdigest()
        verify(b'original', expected)
        with self.assertRaises(ValueError):
            verify(b'modified', expected)

    def test_only_audited_commits_enabled(self):
        self.assertEqual(set(SOURCES.values()), {'2.6.2', '2.8.2.1'})
        self.assertNotIn('972fdbfe9e40853afc09eb06f83045c95acfb53c', SOURCES)

    def test_unknown_source_rejected_before_download(self):
        with patch('restore_legacy.subprocess.check_output', return_value='972fdbfe9e40853afc09eb06f83045c95acfb53c'), \
             patch.dict('os.environ', {'VERSION': '2.6.2'}), \
             patch('restore_legacy.urllib.request.urlopen') as download:
            with self.assertRaises(ValueError):
                main()
            download.assert_not_called()
