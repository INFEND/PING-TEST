from pathlib import Path
import unittest

SERVICE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class NotificationSnapshot(unittest.TestCase):
    def test_bounded_snapshot(self):
        body = SERVICE.split("private static Snapshot notificationSnapshot(){", 1)[1].split("/**", 1)[0]
        self.assertIn("synchronized(LOCK)", body)
        self.assertIn("live.copy(false)", body)
        self.assertIn("s.log.add(live.log.get(live.log.size()-1))", body)
        self.assertNotIn("addAll", body)

    def test_notification_paths(self):
        self.assertIn("makeNotification(notificationSnapshot())", SERVICE)
        self.assertIn("Snapshot s=notificationSnapshot();long now=SystemClock.elapsedRealtime();", SERVICE)

    def test_history_still_full(self):
        self.assertIn("Snapshot s=snapshot();if(s.id==0)return;", SERVICE)

if __name__ == "__main__":
    unittest.main()
