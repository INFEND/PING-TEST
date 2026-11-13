import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVICE = (ROOT / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class ExplicitLossCommitTests(unittest.TestCase):
    def test_unclassified_negative_outcome_is_fatal(self):
        self.assertIn('(rtt<0 && rtt!=-2 && !"Нет ответа".equals(error));', SERVICE)
        self.assertIn('else if(fatal){live.error=error;', SERVICE)

    def test_empty_diagnostic_gets_error_message(self):
        self.assertIn('if(rtt<0 && rtt!=-2 && !"Нет ответа".equals(error) && error.isEmpty())', SERVICE)
        self.assertIn('error="Неоднозначный результат ping";', SERVICE)

if __name__ == "__main__":
    unittest.main()
