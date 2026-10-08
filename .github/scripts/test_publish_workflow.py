"""Exercise the actual publication shell with a fake gh; never publish test assets."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import yaml


class PublicationTests(unittest.TestCase):
    def invoke(self, rolling, fail_upload=False):
        workflow = yaml.safe_load((Path(__file__).resolve().parents[1] /
                                   'workflows/sign-publish-apks.yml').read_text(encoding='utf-8'))
        script = next(s['run'] for s in workflow['jobs']['publish']['steps']
                      if s.get('name') == 'Publish verified APKs')
        fake = '''
gh() {
  printf '%s\\n' "$*" >> calls.txt
  case "$2" in
    view) printf 'false\\n' ;;
    upload) test "$FAIL_UPLOAD" != true ;;
    *) return 0 ;;
  esac
}
'''
        bash = os.environ.get('TEST_BASH') or shutil.which('bash')
        if not bash:
            self.skipTest('bash is unavailable')
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, 'RUNNER_TEMP': '.', 'RELEASE_TAG': 'upstream-dev' if rolling else 'official-tag',
                   'RELEASE_TITLE': 'AAPS dev – nieuwste build (4.0.0-dev-d)',
                   'SOURCE_REF': 'dev', 'SOURCE_COMMIT': 'b' * 40,
                   'CONTROLLER_SHA': 'c' * 40, 'GITHUB_REPOSITORY': 'owner/repo',
                   'GITHUB_RUN_ID': '123', 'ANDROID_NOTE': 'API 31',
                   'SOURCE_REPOSITORY': 'nightscout/AndroidAPS', 'PRERELEASE': 'true',
                   'ROLLING': str(rolling).lower(), 'FAIL_UPLOAD': str(fail_upload).lower(),
                   'ASSET_TAG': 'upstream-dev-' + 'b' * 40 if rolling else 'official-tag'}
            result = subprocess.run([bash, '--noprofile', '--norc'], input=fake + script,
                                    text=True, capture_output=True, cwd=directory, env=env)
            calls = (Path(directory) / 'calls.txt').read_text()
            return result, calls

    def test_published_rolling_release_is_updated_after_upload(self):
        result, calls = self.invoke(True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('aaps-upstream-dev-' + 'b' * 40 + '.apk', calls)
        self.assertIn('aaps-wear-upstream-dev-' + 'b' * 40 + '.apk', calls)
        self.assertLess(calls.index('release upload'), calls.index('release edit'))
        self.assertIn('--notes-file', calls)

    def test_failed_upload_does_not_publish_new_notes_or_delete_old_assets(self):
        result, calls = self.invoke(True, fail_upload=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('release edit', calls)
        self.assertNotIn('delete', calls)

    def test_published_official_release_is_not_overwritten(self):
        result, calls = self.invoke(False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('release upload', calls)
        self.assertNotIn('release edit', calls)


if __name__ == '__main__':
    unittest.main()
