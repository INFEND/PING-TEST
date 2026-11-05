"""Static regression guard for interrupted native ping cleanup."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'app/src/main/java/com/xarkon/pingtest/PingService.java'


class NativePingCleanupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')

    def test_live_child_is_force_killed_on_any_exit_path(self):
        self.assertIn('finally{if(process!=null){activePings.remove(process);', self.source)
        self.assertIn('if(process.isAlive())process.destroyForcibly();else process.destroy();', self.source)

    def test_interrupted_wait_is_preserved(self):
        self.assertIn('catch(InterruptedException e){Thread.currentThread().interrupt();', self.source)

    def test_normal_ping_reply_still_parsed(self):
        self.assertIn('parseIcmpReply(output,probeAddress)', self.source)


if __name__ == '__main__':
    unittest.main()
