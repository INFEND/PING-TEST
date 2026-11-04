"""Regression checks for explicit java.lang.Process references in Android services."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / 'app/src/main/java/com/xarkon/pingtest/PingService.java').read_text(encoding='utf-8')

class ProcessTypeResolutionTests(unittest.TestCase):
    def test_active_process_collection_uses_java_lang_process(self):
        self.assertIn('Set<java.lang.Process> activePings', SOURCE)
        self.assertIn('ConcurrentHashMap<java.lang.Process,Boolean>', SOURCE)

    def test_termination_loop_uses_java_lang_process(self):
        self.assertIn('for(java.lang.Process process:activePings)', SOURCE)

    def test_no_unqualified_process_declarations(self):
        self.assertIsNone(re.search(r'(?<![.\\w])Process\\s+\\w+', SOURCE))

if __name__ == '__main__':
    unittest.main()
