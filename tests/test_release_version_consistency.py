"""Guard against OTA runs where Gradle version and changelog index diverge."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReleaseVersionConsistency(unittest.TestCase):
    def test_gradle_version_is_indexed(self):
        gradle = (ROOT / "app/build.gradle").read_text(encoding="utf-8")
        version = re.search(r"\bversionName\s+['\"]([^'\"]+)['\"]", gradle)
        code = re.search(r"\bversionCode\s+(\d+)", gradle)
        self.assertIsNotNone(version, "Missing versionName")
        self.assertIsNotNone(code, "Missing versionCode")
        index = json.loads((ROOT / "release_notes/versions.json").read_text(encoding="utf-8"))
        self.assertEqual(index.get(version.group(1)), int(code.group(1)),
                         "Gradle version must match release_notes/versions.json")
        notes = ROOT / "release_notes" / ("v" + version.group(1) + ".txt")
        self.assertTrue(notes.is_file(), "Current version release notes missing")
        self.assertTrue(any(line.lstrip().startswith(("• ", "[+] ", "[-] ", "[=] "))
                            for line in notes.read_text(encoding="utf-8").splitlines()),
                        "Current version has no visible release notes")


if __name__ == "__main__":
    unittest.main()
