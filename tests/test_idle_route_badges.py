from pathlib import Path


SOURCE = Path('app/src/main/java/com/xarkon/pingtest/VpnGuard.java').read_text(encoding='utf-8')


def test_idle_route_badges_are_short_and_russian():
    assert 'case VPN: return "● ЧЕРЕЗ VPN";' in SOURCE
    assert 'case DIRECT: return "● БЕЗ VPN";' in SOURCE
    assert 'default: return "● МАРШРУТ НЕИЗВЕСТЕН";' in SOURCE


def test_uid_route_remains_authoritative():
    assert 'cm.getActiveNetwork()' in SOURCE
    assert 'getAllNetworks()' not in SOURCE
    assert 'return Route.UNKNOWN;' in SOURCE


def test_verbose_idle_copy_removed():
    assert 'сеть по умолчанию для приложения' not in SOURCE
