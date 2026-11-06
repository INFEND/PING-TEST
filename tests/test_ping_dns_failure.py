from pathlib import Path

SOURCE = Path("app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

def test_dns_failures_are_local_errors():
    assert 'else if(isDnsFailure(output))error="Не удалось разрешить адрес узла";' in SOURCE
    assert 'String text=output.toLowerCase(Locale.ROOT);' in SOURCE
    for message in (
        "unknown host", "bad address", "name or service not known",
        "temporary failure in name resolution", "nodename nor servname provided",
        "name resolution failed",
    ):
        assert 'text.contains("' + message + '")' in SOURCE

def test_network_failures_are_local_errors():
    assert 'else if(isNetworkFailure(output))error="Сеть недоступна";' in SOURCE
    for message in ("network is unreachable", "no route to host", "network is down", "network unreachable", "host is unreachable", "host unreachable", "address family not supported by protocol", "protocol not supported", "socket: permission denied", "destination host unreachable", "destination net unreachable", "destination network unreachable", "destination unreachable"):
        assert 'text.contains("' + message + '")' in SOURCE

def test_dns_failure_excluded_from_packet_loss():
    assert 'error.startsWith("Не удалось разрешить адрес узла")' in SOURCE
    assert SOURCE.index('error.startsWith("Не удалось разрешить адрес узла")') < SOURCE.index('if(rtt>=0){', SOURCE.index('boolean fatal='))

def test_real_unanswered_probe_still_counts_as_loss():
    assert 'else if(exitCode==1)error="Нет ответа"' in SOURCE
    assert 'else{live.lost++;addProbeEvent(seq,-1,probeBytes,error);}' in SOURCE

def test_destination_unreachable_is_not_a_timeout():
    assert 'else if(isNetworkFailure(output))error="Сеть недоступна";' in SOURCE
    assert SOURCE.index('else if(isNetworkFailure(output))') < SOURCE.index('else if(exitCode==1)error="Нет ответа"')
    assert 'error.startsWith("Сеть недоступна")' in SOURCE
