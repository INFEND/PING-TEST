import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class ContradictoryReplyLossRegression(unittest.TestCase):
    def test_zero_received_summary_must_not_override_valid_echo(self):
        self.assertIn('exitCode==1&&isConfirmedNoReply(output)&&parseIcmpReply(output,probeAddress)==null', SOURCE)
        self.assertIn('else if(exitCode==1)error="Неоднозначный результат ping (код 1)"', SOURCE)
        self.assertIn('double[] parsed=exitCode==0?parseIcmpReply(output,probeAddress):null;', SOURCE)

    def test_reply_parser_requires_selected_address_and_sequence(self):
        self.assertIn('Pattern.quote(expectedAddress)', SOURCE)
        self.assertIn('Matcher lines=reply.matcher(output)', SOURCE)
        self.assertIn('Matcher time=TIME.matcher(line)', SOURCE)

if __name__ == "__main__":
    unittest.main()
