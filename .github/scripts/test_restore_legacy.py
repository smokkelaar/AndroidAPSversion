import hashlib
import os
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from restore_legacy import verify, SOURCES, main


class LegacyRestorationTests(unittest.TestCase):
    def test_changed_dependency_rejected(self):
        expected = hashlib.sha256(b'original').hexdigest()
        verify(b'original', expected)
        with self.assertRaises(ValueError):
            verify(b'modified', expected)

    def test_only_audited_commits_enabled(self):
        self.assertEqual(SOURCES, {
            'fb9325384e96cdf3b508468584156aa9971638da': '2.8.2.1',
            '408329db4c833c47bafe4c7971fdbc1d5dc076ce': '2.6.2',
        })

    def test_unknown_source_rejected_before_download(self):
        with patch('restore_legacy.subprocess.check_output', return_value='972fdbfe9e40853afc09eb06f83045c95acfb53c'), \
             patch.dict('os.environ', {'VERSION': '2.6.2'}), \
             patch('restore_legacy.urllib.request.urlopen') as download:
            with self.assertRaises(ValueError):
                main()
            download.assert_not_called()

    def test_verified_artifacts_and_environment_written(self):
        payload = b'verified fixture artifact'
        dependencies = [('com.google.android', 'flexbox', '0.3.0',
                         'https://example.invalid/fixture.aar', hashlib.sha256(payload).hexdigest())]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch('restore_legacy.subprocess.check_output', return_value='fb9325384e96cdf3b508468584156aa9971638da'), \
                 patch.dict(os.environ, {'VERSION': '2.8.2.1', 'RUNNER_TEMP': directory, 'GITHUB_ENV': str(root / 'env')}), \
                 patch('restore_legacy.DEPENDENCIES', dependencies), \
                 patch('restore_legacy.urllib.request.urlopen') as download:
                download.return_value.__enter__.return_value.read.return_value = payload
                main()
            repository = root / 'legacy-maven'
            artifact = repository / 'com/google/android/flexbox/0.3.0/flexbox-0.3.0.aar'
            self.assertEqual(artifact.read_bytes(), payload)
            pom = ET.parse(artifact.with_suffix('.pom')).getroot()
            self.assertEqual([pom.findtext(key) for key in ['groupId', 'artifactId', 'version', 'packaging']],
                             ['com.google.android', 'flexbox', '0.3.0', 'aar'])
            self.assertEqual((root / 'env').read_text(), f'LEGACY_MAVEN={repository}\n')
