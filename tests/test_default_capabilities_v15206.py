from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "app/src/main/java/com/xarkon/pingtest/PingService.java").read_text(encoding="utf-8")

class DefaultCapabilitiesTest(unittest.TestCase):
    def test_only_current_default_callback_can_change_generation(self):
        self.assertIn("if(source!=routeCallback || !Objects.equals(observedNetwork,network))return;", SOURCE)
        self.assertIn("observeDefaultCapabilities(this,network,capabilities);", SOURCE)

    def test_only_vpn_transition_changes_generation(self):
        self.assertIn("capabilities.hasTransport(NetworkCapabilities.TRANSPORT_VPN)", SOURCE)
        self.assertIn("if(observedVpn!=null && observedVpn.booleanValue()!=vpn)routeGeneration++;", SOURCE)
        self.assertIn("observedVpn=vpn;", SOURCE)
        self.assertIn("observedNetwork=next;\n                observedVpn=null;", SOURCE)

if __name__ == "__main__":
    unittest.main()
