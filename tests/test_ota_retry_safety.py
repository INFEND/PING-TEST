"""Guardrails for idempotent OTA release retries."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ota-release.yml"

class OtaRetrySafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_existing_tag_must_match_current_commit(self):
        self.assertIn('if [[ "$TAG_SHA" != "$GITHUB_SHA" ]]', self.workflow)
        self.assertIn('refusing to reuse the tag', self.workflow)

    def test_annotated_tags_are_resolved(self):
        self.assertIn('if [[ "$TAG_TYPE" == "tag" ]]', self.workflow)
        self.assertIn('git/tags/$TAG_SHA', self.workflow)

    def test_both_ota_assets_are_checked_after_retry(self):
        self.assertIn('for asset in PING-TEST.apk update.json; do', self.workflow)
        self.assertIn("grep -Fxq", self.workflow)

    def test_retry_does_not_clobber_existing_assets(self):
        self.assertNotIn('gh release upload "$TAG" --clobber', self.workflow)
        self.assertIn('else\n            gh release create "$TAG"', self.workflow)

if __name__ == "__main__":
    unittest.main()
