"""Read build requirements as data; never evaluate upstream Gradle code."""
import fnmatch
import json
import os
from pathlib import Path
import re


def read_metadata(source, mapping):
    modern = source / 'buildSrc/src/main/kotlin/Versions.kt'
    if modern.exists():
        text = modern.read_text()
        version = re.search(r'const val appVersion\s*=\s*"([^"]+)"', text).group(1)
        minimum = int(re.search(r'const val minSdk\s*=\s*(\d+)', text).group(1))
        compile_sdk = int(re.search(r'const val compileSdk\s*=\s*(\d+)', text).group(1))
    else:
        text = (source / 'app/build.gradle').read_text()
        version = re.search(r'^\s*version\s+"([^"]+)"', text, re.MULTILINE).group(1)
        minimum = int(re.search(r'minSdkVersion\s+(\d+)', text).group(1))
        compile_sdk = int(re.search(r'compileSdkVersion\s+(\d+)', text).group(1))
    if not re.fullmatch(r'[0-9][A-Za-z0-9._-]{0,80}', version):
        raise ValueError('Unexpected upstream version format')
    java = mapping['default']
    for entry in mapping['mappings']:
        if fnmatch.fnmatchcase(version, entry['pattern']):
            java = entry['jdk']
            break
    return {'VERSION': version, 'MIN_SDK': minimum, 'COMPILE_SDK': compile_sdk, 'JAVA_VERSION': java}


def main():
    metadata = read_metadata(Path('.'), json.loads(Path('../controller/.github/jdk-map.json').read_text()))
    with open(os.environ['GITHUB_ENV'], 'a') as environment, open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        for key, value in metadata.items():
            environment.write(f'{key}={value}\n')
            output.write(f'{key.lower()}={value}\n')


if __name__ == '__main__':
    main()
