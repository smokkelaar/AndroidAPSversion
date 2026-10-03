"""Plan new upstream refs; published releases are the durable success ledger."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

UPSTREAM = "nightscout/AndroidAPS"
CHANNELS = ("master", "dev", "dev3")


def read_refs(text):
    refs = dict(line.split()[::-1] for line in text.splitlines() if line.strip())
    # Annotated tags must build the peeled commit, not the tag object.
    return {ref: refs.get(ref + "^{}", sha) for ref, sha in refs.items()
            if not ref.endswith("^{}")}


def release_tag(channel, ref, sha):
    if channel != "tags":
        return f"upstream-{channel}-{sha}"
    label = re.sub(r"[^A-Za-z0-9._-]", "-", ref)[:80]
    digest = hashlib.sha256(ref.encode()).hexdigest()[:12]
    return f"upstream-tag-{label}-{digest}-{sha}"


def plan(baseline, current, published):
    pending = []
    for ref, sha in sorted(current.items()):
        if ref.startswith("refs/heads/"):
            channel = ref.removeprefix("refs/heads/")
            if channel not in CHANNELS or baseline["refs"].get(ref) == sha:
                continue
            name = channel
        elif ref.startswith("refs/tags/"):
            # Existing tags remain excluded even if upstream moves them later.
            if ref in baseline["refs"]:
                continue
            channel, name = "tags", ref.removeprefix("refs/tags/")
        else:
            continue
        tag = release_tag(channel, name, sha)
        if tag not in published:
            pending.append(dict(channel=channel, ref=name, sha=sha, release_tag=tag))
    return pending


def main():
    baseline = json.loads(Path(".github/upstream-baseline.json").read_text())
    refs = subprocess.check_output([
        "git", "ls-remote", f"https://github.com/{UPSTREAM}.git",
        *[f"refs/heads/{c}" for c in CHANNELS], "refs/tags/*"
    ], text=True)
    # gh --paginate --slurp retains every page, including more than 100 releases.
    pages = json.loads(subprocess.check_output([
        "gh", "api", "--paginate", "--slurp",
        f"repos/{os.environ['GITHUB_REPOSITORY']}/releases?per_page=100"
    ], text=True))
    published = {r["tag_name"] for page in pages for r in page if not r["draft"]}
    pending = plan(baseline, read_refs(refs), published)
    # Bound runner usage; remaining new tags are picked up on the next poll.
    batch = pending[:20]
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("matrix=" + json.dumps({"include": batch}) + "\n")
        output.write(f"count={len(batch)}\n")
    print(f"{len(pending)} new refs; building {len(batch)} this run.")


if __name__ == "__main__":
    main()
