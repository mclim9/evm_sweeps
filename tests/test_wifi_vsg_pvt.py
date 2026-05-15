import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.wifi_vsg_pvt import VSG_driver

class TestWiFiVSGPVT(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig used inside wifi_vsg_pvt to avoid socket creation
        self.bench_patcher = patch('driver.wifi_vsg_pvt.BenchConfig')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock the VSG instrument returned by BenchConfig().VSG_start()
        self.mock_vsg = MagicMock()
        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSG_start.return_value = self.mock_vsg

        # Instantiate the driver under test
        self.driver = VSG_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_connects_to_vsg(self):
        """Test that __init__ starts the VSG connection via BenchConfig."""
        self.mock_bench_instance.VSG_start.assert_called_once()
        self.assertEqual(self.driver.VSG, self.mock_vsg)

    def test_init_with_custom_vsg(self):
        """Test that providing a VSG object overrides BenchConfig lookup."""
        custom_vsg = MagicMock()
        driver = VSG_driver(VSG=custom_vsg)
        self.assertEqual(driver.VSG, custom_vsg)
        # BenchConfig().VSG_start() shouldn't be called if VSG is passed manually
        # (The count remains 1 from the call in setUp for self.driver)
        self.assertEqual(self.mock_bench_instance.VSG_start.call_count, 1)

    def test_vsg_configure_sends_commands(self):
        """Test vsg_configure sends the correct SCPI commands."""
        # Note: vsg_configure is decorated with method_timer, which returns (result, elapsed_time)
        result, elapsed = self.driver.vsg_configure()

        self.mock_vsg.write.assert_called_with("SOUR:GPRF:GEN1:STAT ON")
        self.assertIsNone(result)
        self.assertIsInstance(elapsed, float)

    def test_vsg_get_extra_returns_default(self):
        """Test vsg_get_extra returns 'none'."""
        self.assertEqual(self.driver.vsg_get_extra(), "none")

    def test_vsg_save_state_placeholder(self):
        """Test vsg_save_state is callable (currently a placeholder)."""
        self.driver.vsg_save_state()

    def test_vsg_set_frequency(self):
        """Test vsg_set_frequency sends the correct SCPI command."""
        test_freq = 5.8e9
        self.driver.vsg_set_frequency(test_freq)
        self.mock_vsg.write.assert_called_with(f":SOUR:GPRF:GEN1:RFS:FREQ {test_freq}")

    def test_vsg_set_power(self):
        """Test vsg_set_power sends the correct SCPI command."""
        test_pwr = -15.0
        self.driver.vsg_set_power(test_pwr)
        self.mock_vsg.write.assert_called_with(f"SOUR:GPRF:GEN1:RFS:LEV {test_pwr}")

if __name__ == '__main__':
    unittest.main()
