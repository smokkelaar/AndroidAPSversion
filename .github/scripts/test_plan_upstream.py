import unittest
from plan_upstream import plan, read_refs, release_tag


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.refs = {'refs/heads/master': 'a' * 40, 'refs/heads/dev': 'b' * 40,
                     'refs/heads/dev3': 'c' * 40, 'refs/tags/3.4.2.6': 'd' * 40}
        self.baseline = {'refs': self.refs.copy()}

    def test_initial_snapshot_builds_nothing(self):
        self.assertEqual(plan(self.baseline, self.refs, set()), [])

    def test_all_channels_and_new_tag(self):
        current = {ref: 'e' * 40 for ref in self.refs}
        current['refs/tags/4.0.0'] = 'f' * 40
        result = plan(self.baseline, current, set())
        self.assertEqual({r['channel'] for r in result}, {'master', 'dev', 'dev3', 'tags'})
        self.assertEqual(len(result), 4)  # Moved historical tag remains excluded.

    def test_success_is_skipped_but_failure_retries(self):
        current = {**self.refs, 'refs/tags/4.0.0': 'e' * 40}
        pending = plan(self.baseline, current, set())
        self.assertEqual(len(pending), 1)
        self.assertEqual(plan(self.baseline, current, {pending[0]['release_tag']}), [])
        self.assertEqual(plan(self.baseline, current, set()), pending)

    def test_annotated_tags_use_peeled_commit(self):
        self.assertEqual(read_refs('abc refs/tags/4.0\ndef refs/tags/4.0^{}\n'),
                         {'refs/tags/4.0': 'def'})

    def test_sanitized_tag_names_do_not_collide(self):
        self.assertNotEqual(release_tag('tags', 'release/4', 'a' * 40),
                            release_tag('tags', 'release-4', 'a' * 40))


if __name__ == '__main__':
    unittest.main()
