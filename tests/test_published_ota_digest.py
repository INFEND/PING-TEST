import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ota-release.yml"

class PublishedOtaDigestTests(unittest.TestCase):
    def test_published_assets_checked_against_local_sha256(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("for asset in PING-TEST.apk update.json; do", workflow)
        self.assertIn('releases/tags/$TAG', workflow)
        self.assertIn("sha256sum", workflow)
        self.assertIn('published_digest\" != \"$local_digest', workflow)
        self.assertIn("exit 1", workflow)

if __name__ == "__main__":
    unittest.main()
