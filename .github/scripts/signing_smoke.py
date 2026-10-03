"""Test the exact signing step with tiny fixture APKs and throwaway keys."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import yaml


def run(*args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs)


def main():
    sdk = Path(os.environ['ANDROID_HOME'])
    tools = sorted((sdk / 'build-tools').iterdir(), key=lambda p: tuple(int(x) for x in p.name.split('.') if x.isdigit()))[-1]
    platform = sorted((sdk / 'platforms').glob('*/android.jar'))[-1]
    workflow = yaml.safe_load((Path(__file__).resolve().parents[1] / 'workflows/sign-publish-apks.yml').read_text())
    step = next(s for s in workflow['jobs']['publish']['steps'] if s.get('name', '').startswith('Align, sign'))
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        incoming = root / 'incoming'
        incoming.mkdir()
        keystore = root / 'keystore'
        keystore.mkdir()
        manifest = root / 'AndroidManifest.xml'
        manifest.write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="app.fixture.signing"><uses-sdk android:minSdkVersion="23" android:targetSdkVersion="35"/><application android:hasCode="false"/></manifest>''')
        for module in ['phone', 'wear']:
            run(str(tools / 'aapt'), 'package', '-f', '-M', str(manifest), '-I', str(platform), '-F', str(incoming / f'{module}.apk'))
        password = 'fixture-password'
        for filename in ['keystore/keystore.jks', 'previous.jks']:
            run('keytool', '-genkeypair', '-keystore', str(root / filename), '-storepass', password,
                '-keypass', password, '-alias', 'fixture', '-keyalg', 'RSA', '-keysize', '2048',
                '-validity', '1', '-dname', 'CN=Signing Fixture')
        # Wear simulates a debug APK already signed by a different key.
        run(str(tools / 'apksigner'), 'sign', '--ks', str(root / 'previous.jks'),
            '--ks-pass', 'pass:' + password, str(incoming / 'wear.apk'))
        run('keytool', '-exportcert', '-keystore', str(keystore / 'keystore.jks'), '-storepass', password,
            '-alias', 'fixture', '-file', str(root / 'certificate.der'))
        expected = hashlib.sha256((root / 'certificate.der').read_bytes()).hexdigest()
        script = step['run'].replace('d6bf11fc569083e33dfc07733b579e4491beaa4ac3285b80fbe73e03c2691bb8', expected)
        env = {**os.environ, 'RUNNER_TEMP': str(root), 'RELEASE_TAG': 'fixture-test',
               'KEYSTORE_PASSWORD': password, 'KEY_PASSWORD': password, 'KEY_ALIAS': 'fixture', 'MIN_PHONE_SDK': '23'}
        try:
            subprocess.run(['bash', '-euo', 'pipefail', '-c', script], cwd=root, env=env, check=True)
        except subprocess.CalledProcessError:
            print('Available tools:', [(p.name, (p / 'apksigner').exists()) for p in (sdk / 'build-tools').iterdir()], flush=True)
            for log in root.glob('*-verify.txt'):
                print(log.read_text(), flush=True)
            raise
        assert len(list((root / 'signed').glob('*.apk'))) == 2
        print('Unsigned phone and previously signed Wear APKs both re-signed and verified successfully.')
        for apk in (root / 'signed').glob('*.apk'):
            apk.unlink()
        env['MIN_PHONE_SDK'] = '24'
        rejected = subprocess.run(['bash', '-euo', 'pipefail', '-c', script],
                                  cwd=root, env=env, capture_output=True, text=True)
        assert rejected.returncode != 0, 'Mismatched minimum SDK was accepted'
        assert 'Phone minimum SDK mismatch: expected 24, got 23' in rejected.stderr, rejected.stderr
        print('APK with a mismatched minimum SDK rejected before publication.')


if __name__ == '__main__':
    main()
