import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from plan_selected import main

CATALOG = Path(__file__).resolve().parents[1] / 'selected-releases.json'


class SelectionTests(unittest.TestCase):
    def invoke(self, pages):
        # Exercise the actual CLI entry point and GitHub-output serialization.
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'outputs.txt'
            with patch.dict(os.environ, {'GITHUB_REPOSITORY': 'owner/repo', 'GITHUB_OUTPUT': str(output)}), \
                 patch('plan_selected.subprocess.check_output', return_value=json.dumps(pages)) as call, \
                 patch('plan_selected.Path.read_text', return_value=CATALOG.read_text(encoding='utf-8')), \
                 contextlib.redirect_stdout(io.StringIO()):
                main()
                self.assertIn('--paginate', call.call_args.args[0])
                self.assertIn('--slurp', call.call_args.args[0])
            values = dict(line.split('=', 1) for line in output.read_text().splitlines())
            return int(values['count']), json.loads(values['matrix'])['include']

    def test_only_pinned_selection_is_built(self):
        count, pending = self.invoke([[{'tag_name': 'unselected-historical-tag', 'draft': False}]])
        selected = json.loads(CATALOG.read_text(encoding='utf-8'))['releases']
        self.assertEqual(count, 8)
        self.assertEqual(pending, selected)
        self.assertTrue(all(len(entry['sha']) == 40 for entry in pending))

    def test_published_pages_are_skipped_but_drafts_retry(self):
        selected = json.loads(CATALOG.read_text(encoding='utf-8'))['releases']
        pages = [[{'tag_name': selected[0]['release_tag'], 'draft': False}],
                 [{'tag_name': selected[1]['release_tag'], 'draft': True},
                  {'tag_name': selected[2]['release_tag'], 'draft': False}]]
        count, pending = self.invoke(pages)
        self.assertEqual(count, 6)
        tags = {entry['release_tag'] for entry in pending}
        self.assertNotIn(selected[0]['release_tag'], tags)
        self.assertNotIn(selected[2]['release_tag'], tags)
        self.assertIn(selected[1]['release_tag'], tags)

    def test_complete_catalog_has_empty_matrix(self):
        selected = json.loads(CATALOG.read_text(encoding='utf-8'))['releases']
        count, pending = self.invoke([[{'tag_name': e['release_tag'], 'draft': False} for e in selected]])
        self.assertEqual((count, pending), (0, []))
