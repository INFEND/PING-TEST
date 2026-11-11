#!/usr/bin/env python3
"""Regression: native ping exit 0 must not override local failure diagnostics."""
from pathlib import Path

source = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
start = source.index("boolean localFailure=")
end = source.index("if(parsed!=null && !outputTruncated.get()", start)
section = source[start:end]
for marker in ('isNetworkFailure(output)', 'isDnsFailure(output)',
               'diagnostics.contains("sendto:")', 'diagnostics.contains("sendmsg:")',
               'diagnostics.contains("socket:")', 'diagnostics.contains("permission denied")',
               'diagnostics.contains("operation not permitted")',
               'diagnostics.contains("unknown option")', 'diagnostics.contains("invalid option")',
               'diagnostics.contains("usage:")'):
    assert marker in section, f"Missing local failure guard: {marker}"
assert '((exitCode==0||receivedDespiteExitOne)&&!localFailure)' in section
assert 'if(parsed!=null && !outputTruncated.get() && !outputReadFailed.get())' in source
print("PASS: contradictory native ping diagnostics cannot publish RTT")
