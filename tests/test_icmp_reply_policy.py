import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SERVICE=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class IcmpReplyPolicyTests(unittest.TestCase):
    def test_exit_code_is_checked(self):
        self.assertIn("process.exitValue()==0 && hasIcmpReply(output,address)", SERVICE)
    def test_latency_only_on_valid_reply(self):
        self.assertIn("if(validReply&&m.find())", SERVICE)
    def test_ttl_only_on_confirmed_latency(self):
        self.assertIn("if(rtt>=0&&t.find())", SERVICE)
    def test_output_must_match_expected_address(self):
        self.assertIn("Pattern.quote(expectedAddress)", SERVICE)
        self.assertIn("return reply.matcher(output).find();", SERVICE)
    def test_no_fake_fallback_rtt(self):
        self.assertNotIn("rtt=timeout", SERVICE)

if __name__=="__main__":
    unittest.main()
