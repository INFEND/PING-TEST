"""Guard against native ping pipe deadlock and unbounded output buffering."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class PingOutputDrainTests(unittest.TestCase):
    def test_reader_starts_before_wait(self):
        self.assertLess(SOURCE.index('reader.start();'), SOURCE.index('process.waitFor('))
    def test_drain_continues_after_buffer_limit(self):
        self.assertIn('while((read=input.read(temp))!=-1)', SOURCE)
        self.assertIn('int remaining=8192-buffer.size();', SOURCE)
        self.assertIn('if(remaining>0)buffer.write(temp,0,Math.min(read,remaining));', SOURCE)
    def test_timeout_remains_bounded_and_fatal(self):
        self.assertIn('process.waitFor(probeTimeout+3,TimeUnit.SECONDS)', SOURCE)
        self.assertRegex(SOURCE, r'(?s)if\s*\(!finished\)\s*\{.*?process\.destroyForcibly\(\);.*?error="Локальный тайм-аут процесса ping";.*?\}')
        self.assertIn('reader.join(200);', SOURCE)
        self.assertIn('reader.join(1000);', SOURCE)
    def test_reply_parsed_after_reader_completion(self):
        self.assertLess(SOURCE.index('reader.join(1000);'), SOURCE.index('exitCode==0?parseIcmpReply(output,probeAddress):null'))

if __name__ == "__main__":
    unittest.main()
