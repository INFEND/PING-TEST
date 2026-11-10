#!/usr/bin/env python3
"""Indented Android native ping replies remain genuine ICMP responses."""
from pathlib import Path
import re

source = Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
start = source.index("private static double[] parseIcmpReply(")
end = source.index("private static boolean isDnsFailure(", start)
method = source[start:end]
assert r'(?m)^[ \\t]*\\d+ bytes from ' in method, "Only horizontal indentation is allowed"
assert 'Pattern.quote(expectedAddress)' in method
assert r'\\bicmp_seq(?:[ \t]*=[ \t]*|[ \t]+)1(?![\\w.,:/+\\-])' in method

def matches(output, address):
    pattern = re.compile(r"(?m)^[ \t]*\d+ bytes from " + re.escape(address)
                         + r"(?:%[\w.:-]+)?(?::|\s)(?=[^\r\n]*\bicmp_seq(?:[ \t]*=[ \t]*|[ \t]+)1(?![\w.,:/+\-]))[^\r\n]*$", re.I)
    return bool(pattern.search(output))

ip = "1.1.1.1"
assert matches("  64 bytes from 1.1.1.1: icmp_seq=1 ttl=58 time<1", ip)
assert matches("\t64 bytes from 1.1.1.1: icmp_seq=1 ttl=58 time=2.3", ip)
assert matches("64 bytes from 1.1.1.1: icmp_seq=1 ttl=58 time=2.3", ip)
assert not matches(" 64 bytes from 1.1.1.2: icmp_seq=1 ttl=58 time=2.3", ip)
assert not matches("diagnostic: 64 bytes from 1.1.1.1: icmp_seq=1 time=2.3", ip)
assert not matches(" 64 bytes from 1.1.1.1: icmp_seq=2 ttl=58 time=2.3", ip)
assert not matches("64 bytes from 1.1.1.1: icmp_seq=1-2 ttl=58 time=2.3", ip)
print("Indented ICMP echo regression: OK")
