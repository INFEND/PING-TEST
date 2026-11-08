#!/usr/bin/env python3
"""Regression: local ping send failures must never be counted as ICMP loss."""
from pathlib import Path
import re

source = Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
network = re.search(r"private static boolean isNetworkFailure\(String output\)\s*\{(.*?)\n    \}", source, re.S)
assert network, "Network failure classifier missing"
for diagnostic in (
    "cannot assign requested address",
    "no buffer space available",
    "message too long",
    "network interface is down",
):
    assert f'text.contains("{diagnostic}")' in network.group(1), diagnostic

classifier = re.search(r"private static boolean isConfirmedNoReply\(String output\)\s*\{(.*?)\n    \}", source, re.S)
assert classifier and "isNetworkFailure(output)" in classifier.group(1)
assert classifier.group(1).index("isNetworkFailure(output)") < classifier.group(1).index("zeroReceived.matcher(output).find()")
print("PASS: native ping local send errors take precedence over timeout/loss")
