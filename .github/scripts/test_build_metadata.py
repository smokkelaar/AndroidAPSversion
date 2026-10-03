import json
from pathlib import Path
import tempfile
import unittest
from build_metadata import read_metadata

MAPPING = json.loads((Path(__file__).resolve().parents[1] / 'jdk-map.json').read_text())


class MetadataTests(unittest.TestCase):
    def test_current_and_android9_jvm_requirements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            versions = root / 'buildSrc/src/main/kotlin/Versions.kt'
            versions.parent.mkdir(parents=True)
            for version, minimum, sdk, java in [('3.4.2.6', 31, 36, 21), ('3.2.0.4', 28, 34, 17), ('4.0.0-dev-c', 31, 37, 21)]:
                versions.write_text(f'const val appVersion = "{version}"\nconst val minSdk = {minimum}\nconst val compileSdk = {sdk}')
                self.assertEqual(read_metadata(root, MAPPING),
                                 {'VERSION': version, 'MIN_SDK': minimum, 'COMPILE_SDK': sdk, 'JAVA_VERSION': java})

    def test_legacy_groovy_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / 'app/build.gradle'
            app.parent.mkdir()
            for version, minimum in [('2.8.2.1', 26), ('2.6.2', 23)]:
                app.write_text(f'compileSdkVersion 28\n minSdkVersion {minimum}\n version "{version}"')
                result = read_metadata(root, MAPPING)
                self.assertEqual(result['VERSION'], version)
                self.assertEqual(result['MIN_SDK'], minimum)
                self.assertEqual(result['COMPILE_SDK'], 28)
                self.assertEqual(result['JAVA_VERSION'], 11)

    def test_unexpected_version_is_rejected_before_environment_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / 'app/build.gradle'
            app.parent.mkdir()
            app.write_text('compileSdkVersion 28\n minSdkVersion 26\n version "2.8\nJAVA_VERSION=999"')
            with self.assertRaises(ValueError):
                read_metadata(root, MAPPING)
