import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SERVICE=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class IcmpReplyPolicyTests(unittest.TestCase):
    def test_exit_code_is_checked(self):
        self.assertIn("double[] parsed=(exitCode==0||receivedDespiteExitOne)", SERVICE)
        self.assertIn("boolean receivedDespiteExitOne=exitCode==1", SERVICE)
    def test_exit_one_rejects_local_send_failures(self):
        # A contradictory 1/1 summary must not override local send errors.
        policy=SERVICE.split("boolean receivedDespiteExitOne=exitCode==1",1)[1].split("double[] parsed=",1)[0]
        for diagnostic in ("sendto:", "sendmsg:", "socket:"):
            with self.subTest(diagnostic=diagnostic):
                self.assertIn('contains("'+diagnostic+'")',policy)
    def test_latency_only_on_valid_reply(self):
        self.assertIn("if(parsed!=null){rtt=parsed[0];replyTtl=(int)parsed[1];}", SERVICE)
    def test_ttl_only_on_confirmed_latency(self):
        self.assertIn("Matcher ttl=TTL.matcher(line);", SERVICE)
    def test_output_must_match_expected_address(self):
        self.assertIn("Pattern.quote(expectedAddress)", SERVICE)
        self.assertIn("Matcher lines=reply.matcher(output);", SERVICE)
    def test_local_route_failures_not_counted_as_packet_loss(self):
        # Check the case-insensitive helper, not obsolete inline contains() calls.
        helper = SERVICE.split("private static boolean isNetworkFailure(String output){", 1)[1].split("    }", 1)[0]
        self.assertIn("output.toLowerCase(Locale.ROOT)", helper)
        for diagnostic in ("network is unreachable", "no route to host", "network is down"):
            with self.subTest(diagnostic=diagnostic):
                self.assertIn('text.contains("'+diagnostic+'")', helper)
        self.assertIn("else if(isNetworkFailure(output))error=\"Сеть недоступна\";", SERVICE)
        self.assertIn('error.startsWith("Сеть недоступна")', SERVICE)
        self.assertIn('error.equals("Прервано")', SERVICE)
        self.assertIn('else if(fatal){live.error=error;', SERVICE)
        self.assertIn('else{live.lost++;', SERVICE)
    def test_no_fake_fallback_rtt(self):
        self.assertNotIn("rtt=timeout", SERVICE)

if __name__=="__main__":
    unittest.main()
