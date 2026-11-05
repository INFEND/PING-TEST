"""Guardrails for local ping execution failures versus real ICMP loss."""
from pathlib import Path
import re
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class PingLocalFailureRegression(unittest.TestCase):
    def test_process_watchdog_is_not_packet_loss(self):
        # Match the timeout branch semantically, not its old one-line formatting.
        self.assertRegex(SOURCE, r'if\s*\(\s*!finished\s*\)\s*\{[\s\S]*?process\.destroyForcibly\(\);[\s\S]*?error\s*=\s*"Локальный тайм-аут процесса ping";')
        self.assertIn('error.startsWith("Локальный тайм-аут процесса ping")||', SOURCE)

    def test_unparsed_success_is_not_packet_loss(self):
        self.assertIn('else if(exitCode==0)error="Ответ ping не распознан";', SOURCE)
        self.assertIn('error.startsWith("Ответ ping не распознан")||', SOURCE)

    def test_actual_no_reply_remains_loss(self):
        self.assertIn('else if(exitCode==1)error="Нет ответа";', SOURCE)
        self.assertIn('else{live.lost++;addProbeEvent(seq,-1,probeBytes,error);}', SOURCE)

    def test_fatal_outcomes_do_not_enter_graph(self):
        self.assertIn('if(!fatal){live.chart.add(', SOURCE)
        self.assertIn('else if(fatal){live.error=error;addProbeEvent(seq,-1,probeBytes,error);}', SOURCE)

if __name__ == "__main__":
    unittest.main()
