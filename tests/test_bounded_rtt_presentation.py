#!/usr/bin/env python3
"""Bounded ICMP RTT must remain a successful, explicitly bounded measurement."""
from pathlib import Path
s=Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
a=Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
assert "if(rtt>=0||rtt==-2){" in s
assert "live.last=-2;live.previous=-1;" in s
assert "live.chart.add(rtt==-2?-2f:" in s
import re
bounded = re.search(r'if\(next==-2\s*&&\s*kind==0\)\{([^\n]+)\}', a)
assert bounded, "Missing bounded RTT display branch"
body = bounded.group(1)
assert 'shown=next;' in body and 'setText("<1");' in body
assert 'setTextColor(QualityColors.GREEN);' in body and 'return;' in body
assert body.index('motion.cancel()') < body.index('setText("<1");')
assert "boolean bounded=s.last==-2;" in a
assert "double ms=s.last>=0?s.last:s.avg();" in a
assert 'qualityState.setText(bounded?"ОТЛИЧНО"' in a
assert "qualityState.setTextColor(bounded?QualityColors.GREEN" in a
assert "QualityColors.rtt(0.5)" not in a
print("Bounded RTT presentation: OK")
