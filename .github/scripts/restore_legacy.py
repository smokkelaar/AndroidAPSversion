"""Restore unavailable UI dependencies only for the two audited legacy snapshots."""
import hashlib
import os
from pathlib import Path
import subprocess
import urllib.request

SOURCES = {
    'fb9325384e96cdf3b508468584156aa9971638da': '2.8.2.1',
    'd370673441a4c8bd49d154b044c5c9367471b130': '2.6.2',
}
DEPENDENCIES = [
    ('com.google.android', 'flexbox', '0.3.0',
     'https://jitpack.io/com/github/google/flexbox-layout/0.3.0/flexbox-layout-0.3.0.aar',
     '2ac1ef09c753a7dafd5d2610b650d4319a60450bb6516c247365eafa83ce7328'),
    ('com.amulyakhare', 'com.amulyakhare.textdrawable', '1.0.1',
     'https://jitpack.io/com/github/amulyakhare/TextDrawable/558677ea316e60346948b381e5e274f49b00d370/TextDrawable-558677ea316e60346948b381e5e274f49b00d370.aar',
     '64508112366abbbcc1df3cf08624e5818defd787f20785fe8feed3dcf3f95a45'),
    ('me.denley.wearpreferenceactivity', 'wearpreferenceactivity', '0.5.0',
     'https://artifactory.appodeal.com/appodeal-public/me/denley/wearpreferenceactivity/wearpreferenceactivity/0.5.0/wearpreferenceactivity-0.5.0.aar',
     '9f8fb9873aaaca6ecf8fd2d2cb2afa11c0f3962b2077f60de8383152578da6ef'),
]
POM_CHECKSUMS = {
    ('me.denley.wearpreferenceactivity', 'wearpreferenceactivity', '0.5.0'):
        '29332f721e42dcef26dee4c758c0eb61f32171fc5e69942d142d3ec725b63e55',
}


def verify(data, expected):
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Legacy dependency checksum mismatch')


def main():
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    version = os.environ['VERSION']
    if SOURCES.get(sha) != version:
        raise ValueError('Legacy restoration requires an audited source commit')
    repository = Path(os.environ['RUNNER_TEMP']) / 'legacy-maven'
    for group, artifact, version, url, expected in DEPENDENCIES:
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        verify(data, expected)
        folder = repository / group.replace('.', '/') / artifact / version
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f'{artifact}-{version}.aar').write_bytes(data)
        pom_path = folder / f'{artifact}-{version}.pom'
        if (group, artifact, version) in POM_CHECKSUMS:
            with urllib.request.urlopen(url.removesuffix('.aar') + '.pom', timeout=60) as response:
                pom = response.read()
            verify(pom, POM_CHECKSUMS[group, artifact, version])
            pom_path.write_bytes(pom)
        else:
            pom_path.write_text(
                '<project><modelVersion>4.0.0</modelVersion>'
                f'<groupId>{group}</groupId><artifactId>{artifact}</artifactId>'
                f'<version>{version}</version><packaging>aar</packaging></project>')
        print(f'Verified {artifact}: {expected}')
    with open(os.environ['GITHUB_ENV'], 'a') as output:
        output.write(f'LEGACY_MAVEN={repository}\n')


if __name__ == '__main__':
    main()
