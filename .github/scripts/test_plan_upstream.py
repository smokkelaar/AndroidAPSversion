import unittest
from unittest.mock import patch
from plan_upstream import choose_batch, cleanup_rolling, plan, published_keys, read_refs, release_tag


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.refs = {'refs/heads/master': 'a' * 40, 'refs/heads/dev': 'b' * 40,
                     'refs/heads/dev3': 'c' * 40, 'refs/tags/3.4.2.6': 'd' * 40}
        self.baseline = {'refs': self.refs.copy()}

    def test_initial_snapshot_creates_rolling_branches_only(self):
        result = plan(self.baseline, self.refs, set(), {'3.4.2.6'})
        self.assertEqual({r['release_tag'] for r in result},
                         {'upstream-master', 'upstream-dev', 'upstream-dev3'})

    def test_all_channels_and_new_tag(self):
        current = {ref: 'e' * 40 for ref in self.refs}
        current['refs/tags/4.0.0'] = 'f' * 40
        result = plan(self.baseline, current, set(), {'4.0.0', '3.4.2.6'})
        self.assertEqual({r['channel'] for r in result}, {'master', 'dev', 'dev3', 'tags'})
        self.assertEqual(len(result), 4)  # Moved historical tag remains excluded.

    def test_success_is_skipped_but_failure_retries(self):
        current = {'refs/tags/4.0.0': 'e' * 40}
        pending = plan(self.baseline, current, set(), {'4.0.0'})
        self.assertEqual(len(pending), 1)
        self.assertEqual(plan(self.baseline, current, {pending[0]['release_tag']}, {'4.0.0'}), [])
        self.assertEqual(plan(self.baseline, current, set(), {'4.0.0'}), pending)

    def test_only_published_official_releases_are_selected(self):
        current = {'refs/tags/4.0.0': 'a' * 40,
                   'refs/tags/4.0.0-rc1': 'b' * 40,
                   'refs/tags/unreleased': 'c' * 40}
        self.assertEqual([r['ref'] for r in plan(self.baseline, current, set(), {'4.0.0'})], ['4.0.0'])
        self.assertEqual(plan(self.baseline, current, set(), set()), [])

    def test_rolling_notes_prevent_rebuild_and_new_head_updates_same_tag(self):
        sha = 'b' * 40
        pages = [[{'tag_name': 'upstream-dev', 'draft': False, 'body': f'Source commit: {sha}\n'}]]
        published = published_keys(pages)
        self.assertEqual(plan(self.baseline, {'refs/heads/dev': sha}, published, set()), [])
        pending = plan(self.baseline, {'refs/heads/dev': 'e' * 40}, published, set())
        self.assertEqual(pending[0]['release_tag'], 'upstream-dev')
        self.assertEqual(pending[0]['sha'], 'e' * 40)
        pages[0][0]['draft'] = True
        self.assertEqual(published_keys(pages), set())

    def test_legacy_branch_history_does_not_block_migration(self):
        sha = 'b' * 40
        pages = [[{'tag_name': f'upstream-dev-{sha}', 'draft': False}]]
        self.assertEqual(len(plan(self.baseline, {'refs/heads/dev': sha}, published_keys(pages), set())), 1)

    def test_cleanup_preserves_other_channels_and_official_releases(self):
        sha = 'b' * 40
        key = f'upstream-dev-{sha}'
        rolling = {'id': 1, 'tag_name': 'upstream-dev', 'draft': False,
                   'body': f'Source commit: {sha}\n', 'assets': [
                       {'id': 10, 'name': f'aaps-{key}.apk'},
                       {'id': 11, 'name': f'aaps-wear-{key}.apk'},
                       {'id': 12, 'name': 'aaps-upstream-dev-' + 'a' * 40 + '.apk'}]}
        pages = [[rolling, {'id': 2, 'tag_name': 'upstream-dev-' + 'a' * 40, 'draft': False},
                  {'id': 3, 'tag_name': 'upstream-dev3-' + 'a' * 40, 'draft': False},
                  {'id': 4, 'tag_name': 'upstream-tag-4.0.0-abc', 'draft': False},
                  {'id': 5, 'tag_name': 'manual-123', 'draft': False}]]
        with patch('plan_upstream.api') as call:
            cleanup_rolling(pages, 'owner/repo')
            self.assertEqual([c.args[0] for c in call.call_args_list], [
                'repos/owner/repo/releases/assets/12', 'repos/owner/repo/releases/2',
                'repos/owner/repo/git/refs/tags/upstream-dev-' + 'a' * 40])
        for damage in ['draft', 'missing-apk', 'missing-commit']:
            with self.subTest(damage=damage), patch('plan_upstream.api') as call:
                broken = {**rolling}
                if damage == 'draft': broken['draft'] = True
                if damage == 'missing-apk': broken['assets'] = rolling['assets'][:1]
                if damage == 'missing-commit': broken['body'] = ''
                cleanup_rolling([[broken, pages[0][1]]], 'owner/repo')
                call.assert_not_called()

    def test_annotated_tags_use_peeled_commit(self):
        self.assertEqual(read_refs('abc refs/tags/4.0\ndef refs/tags/4.0^{}\n'),
                         {'refs/tags/4.0': 'def'})

    def test_sanitized_tag_names_do_not_collide(self):
        self.assertNotEqual(release_tag('tags', 'release/4', 'a' * 40),
                            release_tag('tags', 'release-4', 'a' * 40))

    def test_failures_do_not_starve_later_tags(self):
        pending = [{'release_tag': f'tag-{i:03}'} for i in range(65)]
        attempts = {}
        seen = set()
        for _ in range(4):
            batch, attempts = choose_batch(pending, attempts)
            self.assertEqual(len(batch), 20)
            seen.update(item['release_tag'] for item in batch)
        self.assertEqual(len(seen), 65)  # Even when EVERY attempt fails.

    def test_new_tag_precedes_repeated_failure(self):
        pending = [{'release_tag': 'old'}, {'release_tag': 'new'}]
        batch, updated = choose_batch(pending, {'old': 7}, limit=1)
        self.assertEqual(batch, [{'release_tag': 'new'}])
        self.assertEqual(updated, {'old': 7, 'new': 8})

    def test_rotation_survives_serialization_and_success_removal(self):
        import json
        pending = [{'release_tag': 'a'}, {'release_tag': 'b'}, {'release_tag': 'c'}]
        first, attempts = choose_batch(pending, {}, limit=1)
        attempts = json.loads(json.dumps(attempts))
        second, attempts = choose_batch(pending[1:], attempts, limit=1)
        self.assertEqual(first[0]['release_tag'], 'a')
        self.assertEqual(second[0]['release_tag'], 'b')
        self.assertNotIn('a', attempts)

    def test_empty_queue_removes_all_stale_entries(self):
        self.assertEqual(choose_batch([], {'published': 1, 'superseded': 2}), ([], {}))


if __name__ == '__main__':
    unittest.main()
