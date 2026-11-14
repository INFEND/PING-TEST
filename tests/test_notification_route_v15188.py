from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class NotificationRouteTest(unittest.TestCase):
    def test_notification_requires_explicit_direct_route(self):
        body = SOURCE.split("private Notification makeNotification(Snapshot s){", 1)[1]
        self.assertIn('"VPN включён".equals(s.vpnInfo)?"С VPN":', body)
        self.assertIn('"Сеть приложения без VPN".equals(s.vpnInfo)?"Без VPN":"Сеть неизвестна";', body)
        self.assertNotIn('?"Сеть неизвестна":"Без VPN"', body)

    def test_all_loss_preserves_route_and_warning(self):
        self.assertIn('if(s.ok==0&&s.lost>0&&s.error.isEmpty()&&s.warning.isEmpty())content=routeLabel+" · 0 / "+classified+" • ответов нет";', SOURCE)

if __name__ == "__main__":
    unittest.main()
