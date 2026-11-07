"""Prevent file-transfer instructions leaking into PING TEST network diagnostics."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/ErrorText.java").read_text(encoding="utf-8")


class PingErrorMessagesTests(unittest.TestCase):
    def test_no_file_transfer_advice(self):
        for phrase in ("Откройте QR LINK", "Непереданные файлы",
                       "устройствах поблизости", "готов к передаче"):
            self.assertNotIn(phrase, SOURCE)

    def test_network_specific_diagnostics(self):
        for phrase in ("Удалённый узел отклонил соединение",
                       "Нет маршрута до узла",
                       "Превышено время ожидания ответа от узла",
                       "Соединение прервалось. Проверьте стабильность сети"):
            self.assertIn(phrase, SOURCE)


if __name__ == "__main__":
    unittest.main()
