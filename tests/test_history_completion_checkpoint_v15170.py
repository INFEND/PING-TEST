from pathlib import Path
import unittest
SRC=(Path(__file__).resolve().parents[1]/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
class CompletionCheckpoint(unittest.TestCase):
    def test_checkpoint_counts_committed_completions(self):
        body=SRC.split("boolean routeChangedAtCommit=false;",1)[1].split("private static void addLog",1)[0]
        self.assertLess(body.index("if(!routeChangedAtCommit)"),body.index("live.done++;"))
        self.assertLess(body.index("live.done++;"),body.index("historyCheckpoint=live.done%10==0;"))
        self.assertLess(body.index("historyCheckpoint=live.done%10==0;"),body.index("if(historyCheckpoint)persist(false,capturedRun);"))
        self.assertNotIn("seq%10",body)
if __name__=="__main__": unittest.main()
