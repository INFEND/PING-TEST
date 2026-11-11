#!/usr/bin/env python3
"""Regression guard: partial native ping diagnostics must never publish RTT."""
from pathlib import Path

source = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")
guard = "if(parsed!=null && !outputTruncated.get() && !outputReadFailed.get())"
assert guard in source, "Incomplete ping output could publish a parsed RTT"
assert source.index(guard) < source.index("if(rtt<0&&rtt!=-2)"), (
    "Incomplete-output guard must run before local-error classification"
)
assert 'if(outputTruncated.get())error="Вывод ping превышает 8 КиБ"' in source
assert 'else if(outputReadFailed.get())error="Не удалось полностью прочитать вывод ping"' in source
print("PASS: incomplete ping output cannot publish RTT or masquerade as packet loss")
