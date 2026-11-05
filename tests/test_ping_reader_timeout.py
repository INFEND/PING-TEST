"""Regression guard for native ping reader cleanup after a local timeout."""
from pathlib import Path
import re

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")


def test_timeout_destroys_process_and_closes_reader_pipe():
    branch = re.search(r"if\(!finished\)\{(?P<body>.*?)\}\s*else\{", SOURCE, re.S)
    assert branch, "Native ping timeout branch missing"
    body = branch.group("body")
    assert "process.destroyForcibly()" in body
    assert "input.close()" in body
    assert "reader.join(200)" in body
    assert body.index("process.destroyForcibly()") < body.index("input.close()") < body.index("reader.join(200)")


def test_timeout_is_not_counted_as_packet_loss():
    assert 'error="Локальный тайм-аут процесса ping"' in SOURCE
    assert 'error.startsWith("Локальный тайм-аут процесса ping")' in SOURCE
