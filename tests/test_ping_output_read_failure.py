"""Guard against reporting a lost packet when native ping output could not be read."""
from pathlib import Path

source = (Path(__file__).resolve().parents[1] / 'app/src/main/java/com/xarkon/pingtest/PingService.java').read_text(encoding='utf-8')
assert 'outputReadFailed.set(true);' in source
assert 'else if(outputReadFailed.get())error="Не удалось полностью прочитать вывод ping";' in source
assert source.index('else if(outputReadFailed.get())') < source.index('else if(exitCode==1)error="Нет ответа";')
print('PASS: incomplete ping output is a local error before timeout classification')
