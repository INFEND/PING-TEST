import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
S=(ROOT/"app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
U=(ROOT/"app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
class BoundedRtt(unittest.TestCase):
 def test_bounded_is_success(self):
  for x in ("if(rtt>=0||rtt==-2)","if(rtt<0&&rtt!=-2)","live.timed++","return timed==0?-1:total/timed;","else{live.last=-1;live.previous=-1;}"): self.assertIn(x,S)
 def test_display(self):
  self.assertIn('rtt==-2?"<1 мс"',S)
  self.assertIn('e.latencyMs==-2?"<1 мс"',U)
  self.assertIn('j.put("timed",s.timed)',S)
if __name__=="__main__": unittest.main()
