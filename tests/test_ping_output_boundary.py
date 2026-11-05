"""Regression checks for the 8 KiB native ping diagnostic capture boundary."""
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'app/src/main/java/com/xarkon/pingtest/PingService.java'
code = SOURCE.read_text(encoding='utf-8')
assert 'new java.util.concurrent.atomic.AtomicBoolean(false)' in code
assert 'if(read>remaining)outputTruncated.set(true);' in code
assert 'if(remaining>0)buffer.write(temp,0,Math.min(read,remaining));' in code
assert 'if(outputTruncated.get())error="Вывод ping превышает 8 КиБ";' in code
assert 'if(buffer.size()>=8192)error="Вывод ping превышает 8 КиБ";' not in code
print('PASS: exact 8192 bytes are not treated as truncation; excess bytes are tracked')
