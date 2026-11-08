#!/usr/bin/env python3
"""Regression guard: a bare native ping timeout is not proof of ICMP loss."""
from pathlib import Path
import re

source = Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
start = source.index("private static boolean isConfirmedNoReply(")
end = source.index("\n    private void probe(", start)
method = source[start:end]

# A -c 1 invocation must report exactly one transmitted echo and zero received.
assert "zeroReceived.matcher(output).find()" in method
assert "zeroTransmitted.matcher(output).find()" in method
assert "positiveReceived.matcher(output).find()" in method
assert "reportedErrors.matcher(output).find()" in method
assert r'Pattern reportedErrors=Pattern.compile(\n            "(?i)\\\\+\\\\s*[1-9]\\\\d*\\\\s+errors?\\\\b");' in method, "Java regex literal for +N errors must remain correctly escaped"
assert not re.search(r'if\s*\(\s*text\.contains\("request timeout"\)', method), (
    "A timeout line alone must not count as packet loss"
)

cases = [
    ("Request timeout", False),
    ("Request timeout\n0 packets transmitted, 0 received", False),
    ("Request timeout\n1 packets transmitted, 1 received", False),
    ("Request timeout\n1 packets transmitted, 0 received", True),
    ("1 packets transmitted, 0 received", True),
    ("2 packets transmitted, 0 received", False),
    ("10 packets transmitted, 0 received", False),
    ("1 packets transmitted, 0 received, +1 errors", False),
    ("1 packets transmitted, 0 received, +3 errors", False),
]
summary = re.compile(r"(?m)^\s*1\s+packets? transmitted,\s*0\s+(?:packets? )?received\b", re.I)
for output, expected in cases:
    actual = bool(summary.search(output)) and not bool(re.search(r"\+\s*[1-9]\d*\s+errors?\b", output, re.I))
    assert actual == expected, (output, actual, expected)
print("ICMP timeout summary regression checks: OK")
