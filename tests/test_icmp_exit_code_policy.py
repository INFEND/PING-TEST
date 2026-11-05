import pathlib
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class ExitCodePolicy(unittest.TestCase):
    def test_only_exit_one_counts_as_timeout(self):
        self.assertIn('else if(exitCode==1)error="Нет ответа";', SOURCE)
        self.assertNotIn('else if(exitCode>=2)error=', SOURCE)
    def test_other_codes_are_local_errors(self):
        self.assertIn('else error="Локальная ошибка ping (код "+exitCode+")";', SOURCE)
        self.assertIn('error.startsWith("Локальная ошибка ping")', SOURCE)
    def test_unparsed_success_is_not_packet_loss(self):
        self.assertIn('else if(exitCode==0)error="Ответ ping не распознан";', SOURCE)
        self.assertIn('error.startsWith("Ответ ping не распознан")', SOURCE)

if __name__ == "__main__": unittest.main()
