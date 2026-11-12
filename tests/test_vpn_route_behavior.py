"""Execute the real VpnGuard against minimal Android API doubles (not device tests)."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "app/src/main/java/com/xarkon/pingtest/VpnGuard.java"

class VpnRouteBehavior(unittest.TestCase):
    def test_real_java_route_classifier(self):
        sources = {
            "android/content/Context.java": """package android.content;
public class Context {
 public static final String CONNECTIVITY_SERVICE = "connectivity";
 public Object service;
 public Object getSystemService(String name) { return service; }
}""",
            "android/net/Network.java": """package android.net;
public class Network {}""",
            "android/net/ConnectivityManager.java": """package android.net;
public class ConnectivityManager {
 public Network network;
 public NetworkCapabilities caps;
 public boolean fail;
 public Network getActiveNetwork() {
  if (fail) throw new SecurityException();
  return network;
 }
 public NetworkCapabilities getNetworkCapabilities(Network n) {
  if (n != network) throw new AssertionError("wrong network");
  return caps;
 }
}""",
            "android/net/NetworkCapabilities.java": """package android.net;
public class NetworkCapabilities {
 public static final int TRANSPORT_VPN=4, TRANSPORT_WIFI=1,
 TRANSPORT_CELLULAR=0, TRANSPORT_ETHERNET=3, TRANSPORT_BLUETOOTH=2,
 NET_CAPABILITY_NOT_VPN=15;
 public int transports;
 public boolean notVpn;
 public boolean hasTransport(int t) { return (transports & (1 << t)) != 0; }
 public boolean hasCapability(int c) { return c == NET_CAPABILITY_NOT_VPN && notVpn; }
}""",
            "RouteHarness.java": """import android.content.Context;
import android.net.*;
import com.xarkon.pingtest.VpnGuard;
public class RouteHarness {
 static void check(Context c, VpnGuard.Route expected) {
  if (VpnGuard.route(c) != expected || VpnGuard.active(c) != (expected == VpnGuard.Route.VPN))
   throw new AssertionError("expected " + expected);
 }
 public static void main(String[] args) {
  Context c = new Context();
  check(c, VpnGuard.Route.UNKNOWN);
  ConnectivityManager cm = new ConnectivityManager();
  c.service = cm;
  check(c, VpnGuard.Route.UNKNOWN);
  cm.network = new Network();
  check(c, VpnGuard.Route.UNKNOWN);
  cm.caps = new NetworkCapabilities();
  check(c, VpnGuard.Route.UNKNOWN);
  cm.caps.transports = 1 << NetworkCapabilities.TRANSPORT_WIFI;
  check(c, VpnGuard.Route.DIRECT);
  cm.caps.transports = 1 << NetworkCapabilities.TRANSPORT_CELLULAR;
  check(c, VpnGuard.Route.DIRECT);
  cm.caps.transports |= 1 << NetworkCapabilities.TRANSPORT_VPN;
  check(c, VpnGuard.Route.VPN);
  cm.caps.transports = 0;
  cm.caps.notVpn = true;
  check(c, VpnGuard.Route.DIRECT);
  cm.fail = true;
  check(c, VpnGuard.Route.UNKNOWN);
 }
}""",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = []
            for name, content in sources.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                files.append(str(path))
            subprocess.run(["javac", "-encoding", "UTF-8", "-d", tmp,
                            str(SOURCE), *files], check=True, capture_output=True, timeout=60)
            subprocess.run(["java", "-cp", tmp, "RouteHarness"],
                           check=True, capture_output=True, timeout=30)

if __name__ == "__main__":
    unittest.main()
