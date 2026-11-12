import pathlib
import unittest

SRC=(pathlib.Path(__file__).resolve().parents[1] /
     "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class SessionTickGuard(unittest.TestCase):
    def test_scheduler_captures_own_run(self):
        self.assertIn("c.scheduleAtFixedRate(()->tick(expectedRun)", SRC)
        self.assertIn("final int seq;final long capturedRun=scheduledRun;", SRC)
    def test_old_tick_cannot_dispatch_new_run_probe(self):
        self.assertIn("if(stopping || runId!=capturedRun || !live.active ||", SRC)
        self.assertIn("workers.execute(()->probe(seq,capturedRun,probeAddress,probeBytes,probeTtl,probeTimeout));", SRC)
    def test_tick_rechecks_network_after_route_lookup(self):
        tick = SRC.split("private void tick(", 1)[1].split("private static double[] parseIcmpReply", 1)[0]
        lookup = tick.index("VpnGuard.Route currentRoute=VpnGuard.route(this);")
        recheck = tick.index("!initialNetwork.equals(afterTickRoute)")
        self.assertLess(lookup, recheck)
        self.assertLess(recheck, tick.index("seq=++live.planned"))
        self.assertIn("if(stopping || scheduledRun!=runId)return;", tick[lookup:recheck])
        self.assertIn("finishRun(scheduledRun,", tick[recheck:tick.index("seq=++live.planned")])
    def test_completion_uses_callback_run(self):
        self.assertIn("private void checkFinished(long expectedRun)", SRC)
        self.assertIn("runId!=expectedRun", SRC)
        self.assertIn('finishRun(expectedRun,"Завершено");', SRC)
        self.assertNotIn("checkFinished();", SRC)
    def test_skipped_and_probe_completion_keep_run(self):
        self.assertEqual(SRC.count("checkFinished(capturedRun);"), 2)

if __name__=="__main__":
    unittest.main()
