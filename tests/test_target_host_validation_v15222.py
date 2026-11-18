from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/TargetStore.java").read_text(encoding="utf-8")

class TargetHostValidation(unittest.TestCase):
    def test_production_validator(self):
        start = SOURCE.index("    public static boolean validHost(")
        end = SOURCE.index("    public static void save(", start)
        harness = r'''
    public static void main(String[] args) {
        String[] good = {"localhost", "example.com", "example.com.", "a_b.local",
            "1.1.1.1", "255.255.255.255", "::1", "[2001:db8::1]", "::ffff:192.0.2.1"};
        String[] bad = {null, "", "example.com:443", "[example.com]", "[1.1.1.1]",
            "[::1]:443", "1.2.3.999", "127.1", "01.2.3.4", "1.2.3.4.",
            "a..b", "-a.example", "a-.example", "a/b", "a\nb", "a b",
            "2001:::1", "[]", "[::1", "a".repeat(64)+".com"};
        for(String value:good)if(!validHost(value))throw new AssertionError("Rejected: "+value);
        for(String value:bad)if(validHost(value))throw new AssertionError("Accepted: "+value);
    }
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HostHarness.java"
            path.write_text("public class HostHarness {\n" + SOURCE[start:end] + harness + "\n}", encoding="utf-8")
            subprocess.run(["javac", str(path)], check=True)
            subprocess.run(["java", "-cp", tmp, "HostHarness"], check=True)
