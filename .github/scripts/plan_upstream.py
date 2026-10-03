"""Plan new upstream refs; published releases are the durable success ledger."""
import hashlib
import base64
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

UPSTREAM = "nightscout/AndroidAPS"
CHANNELS = ("master", "dev", "dev3")
STATE_BRANCH = "upstream-release-state"


def choose_batch(pending, attempts, limit=20):
    """Least recently attempted first; failures cannot monopolize the batch."""
    ordered = sorted(pending, key=lambda item: (attempts.get(item["release_tag"], 0), item["release_tag"]))
    batch = ordered[:limit]
    pending_tags = {item["release_tag"] for item in pending}
    updated = {tag: sequence for tag, sequence in attempts.items() if tag in pending_tags}
    sequence = max(updated.values(), default=0)
    for item in batch:
        sequence += 1
        updated[item["release_tag"]] = sequence
    return batch, updated


def api(path, method="GET", data=None, missing_ok=False):
    request = Request("https://api.github.com/" + path, method=method,
                      data=json.dumps(data).encode() if data is not None else None,
                      headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                               "Accept": "application/vnd.github+json", "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=60) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404 and missing_ok:
            return None
        raise


def load_attempts(repository):
    path = f"repos/{repository}/contents/release-queue.json"
    entry = api(path + f"?ref={STATE_BRANCH}", missing_ok=True)
    if entry is None:
        return {}, None
    return json.loads(base64.b64decode(entry["content"]))["attempts"], entry["sha"]


def save_attempts(repository, attempts, file_sha):
    # Save BEFORE starting any builds, including builds that fail before drafting a release.
    if api(f"repos/{repository}/git/ref/heads/{STATE_BRANCH}", missing_ok=True) is None:
        api(f"repos/{repository}/git/refs", "POST",
            {"ref": f"refs/heads/{STATE_BRANCH}", "sha": os.environ["GITHUB_SHA"]})
    data = {"message": "Rotate upstream build queue", "branch": STATE_BRANCH,
            "content": base64.b64encode(json.dumps({"attempts": attempts}, sort_keys=True).encode()).decode()}
    if file_sha is not None:
        data["sha"] = file_sha
    # GitHub's SHA check rejects concurrent changes rather than silently losing the ledger.
    api(f"repos/{repository}/contents/release-queue.json", "PUT", data)


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
    attempts, file_sha = load_attempts(os.environ["GITHUB_REPOSITORY"])
    batch, updated = choose_batch(pending, attempts)
    if batch or updated != attempts:
        save_attempts(os.environ["GITHUB_REPOSITORY"], updated, file_sha)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write("matrix=" + json.dumps({"include": batch}) + "\n")
        output.write(f"count={len(batch)}\n")
    print(f"{len(pending)} new refs; building {len(batch)} this run.")


if __name__ == "__main__":
    main()
