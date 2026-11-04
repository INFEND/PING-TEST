import pathlib
import re
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class IcmpTimeTokenValidation(unittest.TestCase):
    def test_no_partial_numeric_rtt(self):
        # Extract the actual Java pattern literal to exercise its numeric policy.
        line = next(line for line in SOURCE.splitlines() if "private static final Pattern TIME =" in line)
        expression = line.split('Pattern.compile("', 1)[1].split('", Pattern.', 1)[0]
        pattern = re.compile(expression.replace('\\\\', '\\'), re.IGNORECASE)
        for valid in ("time=1", "time=1.25", "time=0,42", "time<1"):
            self.assertIsNotNone(pattern.search(valid), valid)
        for invalid in ("time=1e3", "time=1.2.3", "time=1foo", "time=1,2,3", "time=1ms"):
            self.assertIsNone(pattern.search(invalid), invalid)

if __name__ == "__main__": unittest.main()
