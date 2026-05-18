import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add src directory to path for imports
TEST_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(TEST_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from driver.NR5G_FR1_vsa_fsw import VSA_driver

class TestNR5G_FR1_VSA_FSW(unittest.TestCase):
    def setUp(self):
        # Patch BenchConfig to avoid real socket connections during tests
        self.bench_patcher = patch('driver.NR5G_FR1_vsa_fsw.BenchConfig')
        self.mock_bench_class = self.bench_patcher.start()

        # Mock the VSA instrument and its internal socket
        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()

        self.mock_bench_instance = self.mock_bench_class.return_value
        self.mock_bench_instance.VSA_start.return_value = self.mock_vsa

        # Instantiate the driver under test
        self.driver = VSA_driver()
        
        # Note: vsa_set_frequency uses self.VSG which isn't defined in this class's __init__.
        # We provide a mock here to allow testing that method.
        self.mock_vsg = MagicMock()
        self.driver.VSG = self.mock_vsg

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
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW NR5G, "5G NR"; *OPC?')
        self.mock_vsa.write.assert_any_call(':CONF:NR5G:LDIR UL')
        self.mock_vsa.write.assert_any_call(':UNIT:EVM DB')
        self.assertIsInstance(elapsed, float)

    def test_vsa_get_ACLR(self):
        """Test retrieving ACLR data returns expected values."""
        self.mock_vsa.query.side_effect = [
            "",        # from vsa_sweep query (*OPC?)
            "-15.5",   # chPwr
            "-45.2"    # ACLRV
        ]
        (chPwr, ACLRV), _ = self.driver.vsa_get_ACLR()
        self.assertEqual(chPwr, "-15.5")
        self.assertEqual(ACLRV, "-45.2")

    def test_vsa_get_attn_ref(self):
        """Test retrieving attenuation and reference level."""
        self.mock_vsa.query.return_value = "10"
        self.mock_vsa.queryFloat.return_value = 5.0
        attn, refl = self.driver.vsa_get_attn_ref()
        self.assertEqual(attn, "10")
        self.assertEqual(refl, 5.0)

    def test_vsa_get_ch_power(self):
        """Test retrieving channel power from summary."""
        self.mock_vsa.queryFloat.return_value = -10.5
        pwr = self.driver.vsa_get_ch_power()
        self.assertEqual(pwr, -10.5)
        self.mock_vsa.queryFloat.assert_called_with(':FETC:CC1:ISRC:FRAM:SUMM:POW?')

    def test_vsa_get_evm_success(self):
        """Test EVM retrieval on a successful sweep."""
        # vsa_sweep is called, which calls query('*OPC?')
        self.mock_vsa.query.return_value = "1"
        self.mock_vsa.queryFloat.return_value = -50.5
        
        evm, _ = self.driver.vsa_get_evm()
        self.assertEqual(evm, -50.5)

    def test_vsa_get_evm_retry(self):
        """Test that EVM retrieval retries once on failure."""
        self.mock_vsa.query.return_value = "1"
        # Fail the first attempt, succeed on the second
        self.mock_vsa.queryFloat.side_effect = [Exception("Comm error"), -50.5]
        
        evm, _ = self.driver.vsa_get_evm()
        self.assertEqual(evm, -50.5)

    def test_vsa_get_extra(self):
        """Test vsa_get_extra default value."""
        self.assertEqual(self.driver.vsa_get_extra(), 'none')

    def test_vsa_get_waveform_info(self):
        """Test the construction of the waveform configuration string."""
        self.mock_vsa.query.side_effect = [
            "6000000000", "UL", "MIDD", "BW100", "SS30", "273", "Q1K", "OFF", "OFF", "0.015", "1"
        ]
        info = self.driver.vsa_get_waveform_info()
        self.assertIn("6.0GHz", info)
        self.assertIn("UL", info)
        self.assertEqual(self.driver.Wavename, info)

    def test_vsa_set_frequency(self):
        """Test frequency update on both VSA and VSG."""
        self.driver.vsa_set_frequency(3.5e9)
        self.mock_vsa.write.assert_called_with(':SENSE:FREQ:CENT 3500000000.0')
        self.mock_vsg.write.assert_called_with(':SOUR1:FREQ:CW 3500000000.0')

    def test_vsa_set_level_auto(self):
        """Test triggering autolevel."""
        self.driver.vsa_set_level(method='LEV')
        self.mock_vsa.query.assert_called_with(':SENS:ADJ:LEV;*OPC?')

    def test_vsa_save_state(self):
        """Test saving state and opening the remote instrument folder."""
        self.mock_vsa.s.getpeername.return_value = ("192.168.1.50", 5025)
        self.driver.Wavename = "test_config"
        
        with patch('driver.NR5G_FR1_vsa_fsw.os.system') as mock_sys:
            self.driver.vsa_save_state()
            self.mock_vsa.query.assert_any_call('*IDN?')
            mock_sys.assert_called_once_with(r'start \\192.168.1.50\instr')

    def test_vsa_sweep(self):
        """Test triggering a single capture sweep."""
        _, elapsed = self.driver.vsa_sweep()
        self.mock_vsa.write.assert_called_with('INIT:CONT OFF')
        self.mock_vsa.query.assert_called_with('INIT:IMM;*OPC?')
        self.assertIsInstance(elapsed, float)

if __name__ == '__main__':
    unittest.main()