#!/usr/bin/env python3
"""Regression guard for bounded RTT values in native ping output."""
from pathlib import Path
import re

source = Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
start = source.index("private static double[] parseIcmpReply(")
end = source.index("\n    private static boolean isDnsFailure(", start)
method = source[start:end]
assert "line.substring(time.start(),time.start(1)).indexOf('<')>=0" in method, "Bounded RTT must be detected across optional vendor whitespace"
assert "if(!Double.isFinite(latency)||latency<=0||latency>1)continue;" in method, "Loose upper bounds must not become <1 ms"
assert "latency=-2;" in method

def bounded_value(token):
    match = re.fullmatch(r"time<([0-9]+(?:[.,][0-9]+)?)", token)
    if not match:
        return None
    bound = float(match.group(1).replace(",", "."))
    return -2 if 0 < bound <= 1 else None

for token, expected in [
    ("time<0", None), ("time<0.0", None), ("time<0.1", -2), ("time<1", -2),
    ("time<1.1", None), ("time<10", None), ("time<100", None),
]:
    assert bounded_value(token) == expected, token
print("Bounded RTT classification regression: OK")
