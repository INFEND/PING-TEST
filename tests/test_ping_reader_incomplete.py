"""Regression: unfinished ping output reader must not become an ICMP loss."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class ReaderCompletionPolicy(unittest.TestCase):
    def test_reader_checked_after_joins(self):
        branch = SOURCE.split('else{\n                // Process has exited;', 1)[1].split('int exitCode=process.exitValue()', 1)[0]
        self.assertIn('reader.join(1000)', branch)
        self.assertIn('reader.join(200)', branch)
        self.assertIn('if(reader.isAlive())outputReadFailed.set(true);', branch)
        self.assertLess(branch.index('reader.join(200)'), branch.index('if(reader.isAlive())outputReadFailed.set(true);'))

    def test_incomplete_read_is_local_failure(self):
        self.assertLess(SOURCE.index('else if(outputReadFailed.get())'), SOURCE.index('else if(exitCode==1&&isConfirmedNoReply(output))error="Нет ответа";'))
        self.assertIn('error.startsWith("Не удалось полностью прочитать вывод ping")', SOURCE)

if __name__ == "__main__":
    unittest.main()
