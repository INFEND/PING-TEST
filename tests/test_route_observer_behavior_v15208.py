"""Exercise the actual route observer methods with minimal Android type stubs."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class RouteObserverBehavior(unittest.TestCase):
    def test_transitions(self):
        start = SOURCE.index("    private void observeDefaultNetwork(")
        end = SOURCE.index("    private void startRouteMonitor()", start)
        java = """
import java.util.Objects;
public class RouteHarness {
    static class Network {}
    static class ConnectivityManager { static class NetworkCallback {} }
    static class NetworkCapabilities {
        static final int TRANSPORT_VPN=4;
        boolean vpn;
        NetworkCapabilities(boolean vpn){this.vpn=vpn;}
        boolean hasTransport(int transport){return vpn;}
    }
    static final Object LOCK=new Object();
    ConnectivityManager.NetworkCallback routeCallback;
    Network observedNetwork;
    Boolean observedVpn, observedBlocked;
    long routeGeneration;
""" + SOURCE[start:end] + """
    void expect(long expected){
        if(routeGeneration!=expected)throw new AssertionError(routeGeneration+" != "+expected);
    }
    public static void main(String[] args){
        RouteHarness h=new RouteHarness();
        Network a=new Network(), b=new Network();
        ConnectivityManager.NetworkCallback c=new ConnectivityManager.NetworkCallback();
        ConnectivityManager.NetworkCallback stale=new ConnectivityManager.NetworkCallback();
        h.routeCallback=c;
        h.observeDefaultNetwork(c,a,false); h.expect(1);
        h.observeDefaultBlocked(c,a,false); h.expect(1);
        h.observeDefaultBlocked(stale,a,true); h.expect(1);
        h.observeDefaultBlocked(c,b,true); h.expect(1);
        h.observeDefaultBlocked(c,a,true); h.expect(2);
        h.observeDefaultBlocked(c,a,true); h.expect(2);
        h.observeDefaultBlocked(c,a,false); h.expect(3);
        h.observeDefaultCapabilities(c,a,new NetworkCapabilities(false)); h.expect(3);
        h.observeDefaultCapabilities(c,a,new NetworkCapabilities(true)); h.expect(4);
        h.observeDefaultNetwork(c,b,false); h.expect(5);
        h.observeDefaultNetwork(c,a,true); h.expect(5);
        h.observeDefaultBlocked(c,b,true); h.expect(6);
        h.observeDefaultBlocked(c,b,false); h.expect(7);
        h.routeCallback=null;
        h.observeDefaultBlocked(c,b,true); h.expect(7);
    }
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "RouteHarness.java"
            path.write_text(java, encoding="utf-8")
            subprocess.run(["javac", "-encoding", "UTF-8", str(path)], check=True, timeout=60)
            subprocess.run(["java", "-cp", tmp, "RouteHarness"], check=True, timeout=30)

if __name__ == "__main__":
    unittest.main()
