"""Regression checks for the trust boundary between builds and signing."""
from pathlib import Path
import unittest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / 'workflows'


class IsolationTests(unittest.TestCase):
    def test_build_runners_have_no_signing_secrets_or_write_token(self):
        for name in ['aaps-ci.yml', 'branch-ci.yml', 'pr-ci.yml', 'cherry-pick-ci.yml', 'build-upstream-release.yml']:
            with self.subTest(workflow=name):
                workflow = yaml.safe_load((WORKFLOWS / name).read_text(encoding='utf-8'))
                job = workflow['jobs']['build']
                self.assertEqual(job['permissions'], {'contents': 'read'})
                text = yaml.safe_dump(job)
                self.assertNotIn('secrets.', text)
                self.assertNotIn('KEYSTORE', text)
                self.assertNotIn('contents: write', text)
                self.assertNotIn('android.injected.signing', text)
                for step in job['steps']:
                    if step.get('uses', '').startswith('actions/checkout@'):
                        self.assertIs(step['with']['persist-credentials'], False)

    def test_signing_runner_never_checks_out_or_executes_source(self):
        workflow = yaml.safe_load((WORKFLOWS / 'sign-publish-apks.yml').read_text(encoding='utf-8'))
        job = workflow['jobs']['publish']
        self.assertEqual(job['permissions'], {'contents': 'write'})
        for step in job['steps']:
            self.assertNotIn('checkout', step.get('uses', ''))
            self.assertNotIn('gradlew', step.get('run', ''))
            self.assertNotIn('cache', step.get('with', {}))
        signing = next(s for s in job['steps'] if s.get('name', '').startswith('Align, sign'))
        self.assertLess(signing['run'].index('zipalign" -f'), signing['run'].index('apksigner" sign'))
        self.assertIn('apksigner" verify', signing['run'])


if __name__ == '__main__':
    unittest.main()
