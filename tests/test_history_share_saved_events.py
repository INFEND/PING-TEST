"""Regression: history sharing must include only persisted events, never fabricated probes."""
from pathlib import Path

SOURCE = Path("app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text(encoding="utf-8")
HISTORY = SOURCE.split("private void historyDetails(JSONObject obj)", 1)[1].split("private String date(", 1)[0]

def test_saved_events_are_exported():
    assert 'obj.optJSONArray("events")' in HISTORY
    assert 'for(int i=0;i<savedEvents.length();i++)' in HISTORY
    assert 'event.optInt("number",0)' in HISTORY
    assert 'event.optDouble("latencyMs",-1)' in HISTORY
    assert 'event.optString("message","")' in HISTORY
    assert 'String out=report.toString()' in HISTORY
    assert 'copyButton.setOnClickListener(v->copy(out))' in HISTORY
    assert 'shareButton.setOnClickListener(v->share(out))' in HISTORY

def test_legacy_and_missing_history_are_honest():
    assert 'else if(!rawLog.trim().isEmpty())' in HISTORY
    assert 'report.append("\\n").append(rawLog)' in HISTORY
    assert 'События этого сеанса не сохранены.' in HISTORY
