"""Execute production ICMP parser methods in a JVM, without Android dependencies."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class IcmpParserBehavior(unittest.TestCase):
    def test_java_parser(self):
        # Copy the actual contiguous parser methods, not a reimplementation.
        start = SOURCE.index("    private static double[] parseIcmpReply(")
        end = SOURCE.index("    private void probe(", start)
        patterns = "\n".join(line for line in SOURCE.splitlines()
                             if "private static final Pattern TIME =" in line
                             or "private static final Pattern TTL =" in line)
        harness = r'''
    static void reply(String line, double expected, int ttl) {
        double[] result = parseIcmpReply(line, "1.1.1.1");
        if (result == null || result[0] != expected || result[1] != ttl)
            throw new AssertionError(line);
    }
    static void reject(String line) {
        if (parseIcmpReply(line, "1.1.1.1") != null)
            throw new AssertionError(line);
    }
    static void loss(String line, boolean expected) {
        if (isConfirmedNoReply(line) != expected) throw new AssertionError(line);
    }
    public static void main(String[] args) {
        String prefix = "64 bytes from 1.1.1.1: icmp_seq=1 ";
        reply(prefix + "ttl=57 time=12.5 ms", 12.5, 57);
        reply(prefix + "ttl=57 time<1 ms", -2, 57);
        reply(prefix + "time=0,42 ms", 0.42, -1);
        reply(prefix + "ttl=256 time=2 ms", 2, -1);
        reply(prefix + "ttl=64 ttl=32 time=2 ms", 2, -1);
        reply(prefix + "ttl=64 time<1 ms ttl=32", -2, -1);
        reject(prefix + "time<10 ms");
        if (parseIcmpReply(prefix + "time<10 ms", "1.1.1.1", true) == null
                || parseIcmpReply(prefix + "ttl=64", "1.1.1.1", true) == null
                || parseIcmpReply(prefix + "time=2 ms time=90 ms", "1.1.1.1", true) == null)
            throw new AssertionError("Unusable RTT must not erase matching echo evidence");
        if (parseIcmpReply("64 bytes from 1.1.1.2: icmp_seq=1 time=2 ms", "1.1.1.1", true) != null
                || parseIcmpReply(prefix + "icmp_seq=2 time=2 ms", "1.1.1.1", true) != null)
            throw new AssertionError("Wrong address or ambiguous sequence is not matching evidence");
        reject(prefix + "time<0 ms");
        reject(prefix + "time<0,0 ms");
        reply(prefix + "time=0 ms", 0, -1);
        reply(prefix + "time<0.1 ms", -2, -1);
        reject(prefix + "time=1e3 ms");
        reject(prefix + "time=2 ms time=90 ms");
        reject(prefix + "icmp_seq=2 time=2 ms");
        reject("64 bytes from 1.1.1.1: icmp_seq=2 icmp_seq=1 time=2 ms");
        reject(prefix + "icmp_seq=1 time<1 ms");
        reject(prefix + "time<1 ms time=5 ms");
        reject(prefix + "time=2 ms\n" + prefix + "time=9 ms");
        reject(prefix + "time<1 ms\n" + prefix + "time=0.5 ms");
        reply(prefix + "ttl=64 time<1 ms\n" + prefix + "ttl=64 time<1 ms", -2, 64);
        reply(prefix + "ttl=64 time=2 ms\n" + prefix + "ttl=63 time=2 ms", 2, -1);
        if (parseIcmpReply(prefix + "time=2 ms\n" + prefix + "time=9 ms", "1.1.1.1", true) == null)
            throw new AssertionError("Conflicting echoes still disprove zero replies");
        reply(prefix + "ttl=64 time=2 ms", 2, 64);
        reject("64 bytes from 1.1.1.2: icmp_seq=1 time=2 ms");
        reject("64 bytes from 1.1.1.1: icmp_seq=10 time=2 ms");
        reject("rtt min/avg/max = 1/2/3 ms");
        reject("64 bytes from 1.1.1.1:2: icmp_seq=1 time=2 ms");
        if (parseIcmpReply("64 bytes from 2001:db8::1:2: icmp_seq=1 time=2 ms", "2001:db8::1") != null)
            throw new AssertionError("IPv6 prefix is not the selected address");
        if (parseIcmpReply("64 bytes from 2001:db8::1: icmp_seq=1 time=2 ms", "2001:db8::1") == null)
            throw new AssertionError("Valid IPv6 reply");
        if (!hasConflictingReplySummary("2 packets transmitted, 1 received")
                || !hasConflictingReplySummary("1 packets transmitted, 2 received")
                || !hasConflictingReplySummary("1 packets transmitted, 1 received\n2 packets transmitted, 1 received")
                || hasConflictingReplySummary("1 packets transmitted, 1 received")
                || hasConflictingReplySummary(prefix + "time=2 ms"))
            throw new AssertionError("Single-echo success summary policy");
        loss("1 packets transmitted, 0 received", true);
        loss("1 packets transmitted, 0 received\n2 packets transmitted, 0 received", false);
        loss("10 packets transmitted, 0 received\n1 packets transmitted, 0 received", false);
        loss("1 packets transmitted, 0 received\n1 packets transmitted, 0 received", true);
        loss("0 packets transmitted, 0 received", false);
        loss("Request timeout", false);
        loss("unknown option -W\n1 packets transmitted, 0 received", false);
        loss("invalid option\n1 packets transmitted, 0 received", false);
        loss("Usage: ping\n1 packets transmitted, 0 received", false);
        loss("sendto: Permission denied\n1 packets transmitted, 0 received", false);
        loss("1 packets transmitted, 0 received, +1 errors", false);
        loss("1 packets transmitted, 0 received\n1 packets transmitted, 1 received", false);
    }
'''
        java = "import java.util.*;\nimport java.util.regex.*;\npublic class IcmpHarness {\n" + patterns + "\n" + SOURCE[start:end] + harness + "\n}"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "IcmpHarness.java"
            path.write_text(java, encoding="utf-8")
            subprocess.run(["javac", "-encoding", "UTF-8", str(path)], check=True, timeout=60)
            subprocess.run(["java", "-cp", tmp, "IcmpHarness"], check=True, timeout=30)

if __name__ == "__main__":
    unittest.main()
