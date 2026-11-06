from pathlib import Path

SOURCE = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")

def test_history_separates_loss_and_route():
    history = SOURCE.split("private void historyPage()", 1)[1].split("private void historyDetails(", 1)[0]
    assert 'Ui.chip(this,"ПОТЕРИ  "' in history
    assert 'Ui.chip(this,routeLabel,false)' in history
    assert 'lossLabel.setTextColor(completed==0?QualityColors.UNKNOWN:QualityColors.loss(percent))' in history

def test_unknown_route_not_falsely_reported_as_direct():
    history = SOURCE.split("private void historyPage()", 1)[1].split("private void historyDetails(", 1)[0]
    assert 'vpnInfo.isEmpty()?"МАРШРУТ НЕИЗВЕСТЕН":"БЕЗ VPN"' in history
    assert 'vpnInfo.contains("не определён")?"МАРШРУТ НЕИЗВЕСТЕН"' in history
