"""Guard against duplicate OTA releases from multiple commits of one version."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ReleaseTriggerRegression(unittest.TestCase):
    def test_version_gated_push_paths(self):
        workflow = (ROOT / ".github/workflows/ota-release.yml").read_text(encoding="utf-8")
        push_section = workflow.split("  push:", 1)[1].split("\npermissions:", 1)[0]
        self.assertIn("'release_notes/v*.txt'", push_section)
        self.assertNotIn("'app/build.gradle'", push_section)
        self.assertNotIn("'PING_TEST_SOURCE.zip'", push_section)
        self.assertIn("'.github/workflows/ota-release.yml'", push_section)
        for broad in ("'app/**'", "'tests/**'", "'release_notes/**'", "'scripts/**'"):
            self.assertNotIn(broad, push_section)

    def test_release_uses_checked_out_sources_only(self):
        workflow = (ROOT / ".github/workflows/ota-release.yml").read_text(encoding="utf-8")
        self.assertIn("Verify checked-out Android sources", workflow)
        self.assertIn("git rev-parse HEAD", workflow)
        self.assertNotIn("unzip -oq", workflow)
        self.assertNotIn("git push origin HEAD:main", workflow)

    def test_release_rejects_tag_reuse_on_different_commit(self):
        workflow = (ROOT / ".github/workflows/ota-release.yml").read_text(encoding="utf-8")
        self.assertIn('if [[ "$TAG_SHA" != "$GITHUB_SHA" ]]', workflow)
        self.assertIn('refusing to reuse the tag', workflow)

if __name__ == "__main__":
    unittest.main()
