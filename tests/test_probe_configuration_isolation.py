import pathlib
import unittest

SERVICE=(pathlib.Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class ProbeConfigurationIsolationTests(unittest.TestCase):
    def test_worker_receives_immutable_probe_configuration(self):
        self.assertIn("final int probeBytes,probeTtl,probeTimeout;", SERVICE)
        self.assertIn("probeBytes=bytes;probeTtl=ttl;probeTimeout=timeout;", SERVICE)
        self.assertIn("probe(seq,capturedRun,probeAddress,probeBytes,probeTtl,probeTimeout)", SERVICE)
    def test_ping_command_uses_captured_values(self):
        self.assertIn('Integer.toString(probeTimeout),"-s",Integer.toString(probeBytes),"-t",Integer.toString(probeTtl)', SERVICE)
        self.assertIn("process.waitFor(probeTimeout+3,TimeUnit.SECONDS)", SERVICE)
    def test_events_use_original_payload_size(self):
        self.assertIn('addProbeEvent(seq,rtt,probeBytes,"")', SERVICE)
        self.assertIn('addProbeEvent(seq,-1,probeBytes,error)', SERVICE)
        self.assertIn('addProbeEvent(seq,-1,probeBytes,"Пропуск: очередь заполнена")', SERVICE)

if __name__=="__main__":
    unittest.main()
