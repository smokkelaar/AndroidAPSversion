"""One-time selection requested by the owner; does not reset the automatic baseline."""
import json
import os
from pathlib import Path
import subprocess


def main():
    selected = json.loads(Path('.github/selected-releases.json').read_text())['releases']
    pages = json.loads(subprocess.check_output([
        'gh', 'api', '--paginate', '--slurp',
        f"repos/{os.environ['GITHUB_REPOSITORY']}/releases?per_page=100"
    ], text=True))
    published = {release['tag_name'] for page in pages for release in page if not release['draft']}
    pending = [entry for entry in selected if entry['release_tag'] not in published]
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write('matrix=' + json.dumps({'include': pending}) + '\n')
        output.write(f'count={len(pending)}\n')
    print(f'{len(pending)} selected versions remaining; no other historical versions will be built.')


if __name__ == '__main__':
    main()
