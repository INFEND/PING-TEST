"""Source-level regression checks for Android native ping lifecycle."""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'app/src/main/java/com/xarkon/pingtest/PingService.java'

class PingProcessLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding='utf-8')

    def test_process_registered_immediately_after_start(self):
        source = self.source
        self.assertIn('activePings.add(process);', source)
        self.assertLess(source.index('activePings.add(process);'), source.index('process.waitFor('))

    def test_stop_race_terminates_new_process(self):
        self.assertIn('if(stopping || capturedRun!=runId)process.destroyForcibly();', self.source)

    def test_process_removed_on_probe_exit(self):
        self.assertIn('finally{if(process!=null){activePings.remove(process);', self.source)

    def test_stop_and_destroy_terminate_processes(self):
        self.assertGreaterEqual(self.source.count('terminateActivePings();'), 2)
        self.assertIn('for(java.lang.Process process:activePings)', self.source)
        self.assertNotIn('for(Process process:activePings)', self.source)

if __name__ == '__main__':
    unittest.main()
