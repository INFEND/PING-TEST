import pathlib
import re
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class VendorRttWhitespaceRegression(unittest.TestCase):
    def test_time_token_accepts_vendor_spacing_without_partial_numbers(self):
        line = next(line for line in SOURCE.splitlines() if "private static final Pattern TIME =" in line)
        expression = line.split('Pattern.compile("', 1)[1].split('", Pattern.', 1)[0]
        pattern = re.compile(expression.replace('\\\\', '\\'), re.IGNORECASE)
        for token in ("time=1.2", "time = 1.2", "time < 1", "time<1", "time = 0,42"):
            match = pattern.search(token)
            self.assertIsNotNone(match, token)
            if match:
                self.assertEqual('<' in token, '<' in token[match.start():match.start(1)])
        for token in ("time = 1e3", "time < 1ms", "time=1.2.3"):
            self.assertIsNone(pattern.search(token), token)

    def test_bounded_marker_uses_actual_comparison_operator(self):
        self.assertIn("line.substring(time.start(),time.start(1)).indexOf('<')>=0", SOURCE)
        self.assertNotIn("line.charAt(time.start()+4)", SOURCE)

if __name__ == "__main__":
    unittest.main()
