from pathlib import Path

SOURCE = Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

def test_dns_failures_are_local_errors():
    for message in (
        "unknown host", "Unknown host", "bad address",
        "Name or service not known",
        "Temporary failure in name resolution",
        "nodename nor servname provided",
    ):
        assert 'output.contains("' + message + '")' in SOURCE
    assert 'error="Не удалось разрешить адрес узла"' in SOURCE

def test_dns_failure_excluded_from_packet_loss():
    assert 'error.startsWith("Не удалось разрешить адрес узла")' in SOURCE
    assert SOURCE.index('error.startsWith("Не удалось разрешить адрес узла")') < SOURCE.index('if(rtt>=0){', SOURCE.index('boolean fatal='))

def test_real_unanswered_probe_still_counts_as_loss():
    assert 'else if(exitCode==1)error="Нет ответа"' in SOURCE
    assert 'else{live.lost++;addProbeEvent(seq,-1,probeBytes,error);}' in SOURCE
