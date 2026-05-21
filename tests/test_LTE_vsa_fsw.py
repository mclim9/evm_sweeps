from unittest.mock import MagicMock, patch
import unittest
import sys
import os

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.LTE_vsa_fsw import VSA_driver

class TestLTEVSAFSW(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig to avoid real socket connections during tests
        self.bench_patcher = patch('driver.LTE_vsa_fsw.BenchConfig')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock the VSA instrument and its internal socket
        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()

        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSA_start.return_value = self.mock_vsa

        # Link queryInt and queryFloat to use the query mock, mimicking iSocket behavior
        self.mock_vsa.queryInt.side_effect = lambda s: int(self.mock_vsa.query(s))
        self.mock_vsa.queryFloat.side_effect = lambda s: float(self.mock_vsa.query(s))

        # Instantiate the driver under test
        self.driver = VSA_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_sets_up_vsa(self):
        """Test that __init__ starts VSA connection and sets timeout."""
        self.mock_bench_instance.VSA_start.assert_called_once()
        self.assertEqual(self.driver.VSA, self.mock_vsa)
        self.mock_vsa.s.settimeout.assert_called_with(30)

    def test_vsa_configure_sends_scpi(self):
        """Test vsa_configure sends the correct sequence of SCPI commands."""
        # vsa_configure is decorated with method_timer, returns (None, time)
        _, elapsed = self.driver.vsa_configure()

        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW LTE, "LTE";*OPC?')
        self.mock_vsa.write.assert_any_call(':CONF:LTE:LDIR UL;*WAI')
        self.mock_vsa.write.assert_any_call(f':CONF:LTE:UL:CC:BW BW{self.driver.bw}_00;*WAI')
        self.assertIsInstance(elapsed, float)

    def test_vsa_get_ACLR(self):
        """Test retrieving ACLR data returns expected values."""
        # Query is called in vsa_sweep (*OPC?)
        self.mock_vsa.query.return_value = "1"
        self.mock_vsa.queryFloat.side_effect = [
            -10.5,   # chPwr
            -45.0    # ACLRV
        ]

        (chPwr, ACLRV), _ = self.driver.vsa_get_ACLR()
        self.assertEqual(chPwr, -10.5)
        self.assertEqual(ACLRV, -45.0)
        self.mock_vsa.write.assert_any_call(':CONF:LTE:MEAS ACLR')

    def test_vsa_get_evm_retry_logic(self):
        """Test that EVM retrieval retries once on failure."""
        self.mock_vsa.query.return_value = "1" # For vsa_sweep
        # Fail the first attempt, succeed on the second
        self.mock_vsa.queryFloat.side_effect = [Exception("Comm error"), -42.5]

        evm, _ = self.driver.vsa_get_evm()
        self.assertEqual(evm, -42.5)
        self.assertEqual(self.mock_vsa.queryFloat.call_count, 2)

    def test_vsa_get_waveform_info(self):
        """Test construction of LTE info string."""
        self.mock_vsa.query.side_effect = [
            "2500000000", "UL", "FDD", "BW10_00", "QAM256", "50", "0"
        ]
        info = self.driver.vsa_get_waveform_info()
        self.assertIn("2.500GHz", info)
        self.assertIn("UL_FDD", info)
        self.assertEqual(self.driver.Wavename, info)

    def test_vsa_save_state(self):
        """Test saving state and opening remote folder."""
        self.mock_vsa.s.getpeername.return_value = ("192.168.1.10", 5025)
        # Mock waveform info queries
        self.mock_vsa.query.side_effect = ["IDN", "2500000000", "UL", "FDD", "BW5", "Q256", "24", "0", "OK"]

        with patch('driver.LTE_vsa_fsw.os.system') as mock_sys:
            self.driver.vsa_save_state()
            mock_sys.assert_called_once_with(r'start \\192.168.1.10\instr')

    def test_vsa_set_level_adj(self):
        """Test vsa_set_level with LEV mode."""
        # Decorated with method_timer, returns (result, time)
        _, _ = self.driver.vsa_set_level(mode='LEV')
        self.mock_vsa.query.assert_called_with(':SENS:ADJ:LEV;*OPC?')

    def test_vsa_sweep(self):
        """Test triggering a capture sweep."""
        # Decorated with method_timer, returns (result, time)
        _, _ = self.driver.vsa_sweep()
        self.mock_vsa.write.assert_called_with('INIT:CONT OFF')

if __name__ == '__main__':
    unittest.main()
