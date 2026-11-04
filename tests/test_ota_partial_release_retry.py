"""Regression guard for retrying partially published signed OTA releases."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ota-release.yml"

class OtaPartialReleaseRetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.publish = cls.workflow.split("- name: Publish official Release", 1)[1]

    def test_tag_identity_is_checked_before_repair(self):
        self.assertIn('if [[ "$TAG_SHA" != "$GITHUB_SHA" ]]', self.publish)
        self.assertLess(self.publish.index('if [[ "$TAG_SHA" != "$GITHUB_SHA" ]]'),
                        self.publish.index('gh release upload "$TAG"'))

    def test_missing_assets_are_uploaded_without_clobbering(self):
        self.assertIn('if ! gh release view "$TAG"', self.publish)
        self.assertIn('gh release upload "$TAG" "dist/$asset"', self.publish)
        self.assertNotIn('gh release upload "$TAG" --clobber', self.publish)

    def test_both_assets_are_checked_after_upload(self):
        self.assertIn('for asset in PING-TEST.apk update.json; do', self.publish)
        self.assertGreaterEqual(self.publish.count('for asset in PING-TEST.apk update.json; do'), 2)
        self.assertGreater(self.publish.rindex('grep -Fxq "$asset"'),
                           self.publish.index('gh release upload "$TAG"'))

if __name__ == "__main__":
    unittest.main()
