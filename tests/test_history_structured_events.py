from pathlib import Path
root = Path(__file__).resolve().parents[1]
service = (root / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text()
activity = (root / "app/src/main/java/com/xarkon/pingtest/MainActivity.java").read_text()
assert 'j.put("events",recorded)' in service
for key in ('"number"','"latencyMs"','"payloadBytes"','"message"'):
    assert f'item.put({key}' in service
assert 'new PingService.ProbeEvent(number,latency,payload,message)' in activity
assert 'ТЕКСТОВЫЙ ЖУРНАЛ РАННЕЙ ВЕРСИИ' in activity
assert 'if(structured)frame.addView(eventHeader()' in activity
