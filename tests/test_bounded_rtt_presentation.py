#!/usr/bin/env python3
"""Bounded ICMP RTT must remain a successful, explicitly bounded measurement."""
from pathlib import Path
s=Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
a=Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
assert "if(rtt>=0||rtt==-2){" in s
assert "live.last=-2;live.previous=-1;" in s
assert "live.chart.add(rtt==-2?-2f:" in s
assert 'if(next==-2 && kind==0){shown=next;setText("<1");' in a
assert "double ms=s.last==-2?0.5:s.last>=0?s.last:s.avg();" in a
print("Bounded RTT presentation: OK")
