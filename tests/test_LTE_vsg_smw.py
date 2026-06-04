import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.LTE_vsg_smw import VSG_driver

class TestLTEVSGSMW(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig to avoid real socket connections during tests
        self.bench_patcher = patch('driver.LTE_vsg_smw.BenchConfig')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock the VSG instrument and its internal socket
        self.mock_vsg = MagicMock()
        self.mock_vsg.s = MagicMock()

        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSG_start.return_value = self.mock_vsg

        # Instantiate the driver under test
        self.driver = VSG_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_sets_up_vsg(self):
        """Test that __init__ starts VSG connection and sets defaults."""
        self.mock_bench_instance.VSG_start.assert_called_once()
        self.assertEqual(self.driver.VSG, self.mock_vsg)
        self.assertEqual(self.driver.bw, 5)

    def test_vsg_configure_sends_scpi(self):
        """Test vsg_configure sends correct SCPI sequence."""
        _, elapsed = self.driver.vsg_configure()

        self.mock_vsg.write.assert_any_call(':SOUR1:BB:EUTR:STDM LTE')
        self.mock_vsg.write.assert_any_call(':SOUR1:BB:EUTR:STAT 1')
        self.mock_vsg.query.assert_any_call(':SOUR1:CORR:OPT:EVM 1;*OPC?')
        self.assertIsInstance(elapsed, float)

    def test_vsg_get_extra(self):
        """Test vsg_get_extra returns 'none'."""
        self.assertEqual(self.driver.vsg_get_extra(), 'SMW-LTE')

    def test_vsg_set_frequency(self):
        """Test setting VSG CW frequency."""
        self.driver.vsg_set_frequency(2.1e9)
        self.mock_vsg.write.assert_called_with(':SOUR1:FREQ:CW 2100000000.0')

    def test_vsg_set_power(self):
        """Test setting VSG power."""
        self.driver.vsg_set_power(-20.5)
        self.mock_vsg.write.assert_called_with(':SOUR1:POW:POW -20.5')

    def test_vsg_save_state(self):
        """Test vsg_save_state construction of Wavename and SCPI calls."""
        self.mock_vsg.s.getpeername.return_value = ("192.168.1.11", 5025)

        # Mock response sequence for: *IDN?, Link?, Dupl?, Mod?, RBC?, VRB?, BW?, Store/OPC?
        self.mock_vsg.query.side_effect = [
            "IDN", "UP", "FDD", "QAM256", "24", "0", "BW5_00", "OK"
        ]

        with patch('driver.LTE_vsg_smw.os.system') as mock_sys:
            self.driver.vsg_save_state()

            expected_wavename = "LTE_UL_FDD_BW5_00_24RB_0rbo_QAM256"
            self.assertEqual(self.driver.Wavename, expected_wavename)

            self.mock_vsg.query.assert_any_call(
                f':SOUR1:BB:EUTR:SETT:STOR "/var/user/{expected_wavename}";*OPC?'
            )
            mock_sys.assert_called_once_with(r'start \\192.168.1.11\user')

if __name__ == '__main__':
    unittest.main()
