import os
import sys
import unittest
from unittest.mock import MagicMock, patch

TEST_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '..', 'src')))

from src.driver import WiFi_meas


class TestWiFi_Meas(unittest.TestCase):
    def setUp(self):
        self.bench_patcher = patch('src.driver.WiFi_meas.bench')
        self.mock_bench = self.bench_patcher.start()

        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()
        self.mock_vsg = MagicMock()

        self.mock_bench.return_value.VSA_start.return_value = self.mock_vsa
        self.mock_bench.return_value.VSG_start.return_value = self.mock_vsg

        self.driver = WiFi_meas.std_insr_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_starts_instruments_and_sets_timeout(self):
        self.mock_bench.return_value.VSA_start.assert_called_once()
        self.mock_bench.return_value.VSG_start.assert_called_once()
        self.mock_vsa.s.settimeout.assert_called_once_with(30)

    def test_VSA_config_sends_WiFi_setup_commands(self):
        self.driver.VSA_config()

        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':SYST:DISP:UPD ON; *OPC?')
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW WLAN, "WLAN"; *OPC?')
        self.mock_vsa.write.assert_any_call(':INIT:CONT ON')
        self.mock_vsa.write.assert_any_call(':CONF:STAN 11')

    def test_VSA_get_attn_reflvl_reads_attenuation_and_ref(self):
        self.mock_vsa.query.return_value = '12'
        self.mock_vsa.queryFloat.return_value = 1.2

        attn, refl = self.driver.VSA_get_attn_reflvl()

        self.assertEqual(attn, '12')
        self.assertEqual(refl, 1.2)
        self.mock_vsa.query.assert_called_once_with('INP:ATT?')
        self.mock_vsa.queryFloat.assert_called_once_with('DISP:TRAC:Y:SCAL:RLEV?')

    def test_VSA_get_chPwr_returns_default_value(self):
        chPwr = self.driver.VSA_get_chPwr()
        self.assertEqual(chPwr, 999)

    def test_VSA_get_EVM_returns_evm_value(self):
        self.mock_vsa.query.return_value = '3.1,0.5,0.8'

        result = self.driver.VSA_get_EVM()
        evm = result[0] if isinstance(result, tuple) else result

        self.assertEqual(evm, 3.1)
        self.mock_vsa.query.assert_called_with(':FETC:BURS:EVM:DATA:AVER?')

    def test_VSA_get_EVM_handles_invalid_evm(self):
        self.mock_vsa.query.return_value = 'invalid,value'

        result = self.driver.VSA_get_EVM()
        evm = result[0] if isinstance(result, tuple) else result

        self.assertEqual(evm, 999)

    def test_VSA_get_info_formats_string(self):
        self.mock_vsg.query.side_effect = [
            '2400000000',  # freq
            '11be',        # standard
            'BW320',       # bandwidth
            'MCS13',       # MCS
            '100',         # data length
        ]

        info = self.driver.VSA_get_info()

        self.assertEqual(info, '2.4GHz_11be_BW320_MCS13_100A-MPDU')

    def test_VSA_level_lev_uses_query(self):
        self.driver.VSA_level('LEV')
        self.mock_vsa.query.assert_called_with(':CONF:POW:AUTO ONCE;*OPC?')

    def test_VSA_level_evm_uses_query(self):
        self.driver.VSA_level('EVM')
        self.mock_vsa.query.assert_called_with(':CONF:POW:AUTO ONCE;*OPC?')

    def test_VSA_level_manual_sets_ref_level(self):
        self.driver.get_VSA_chPwr = MagicMock(return_value=20.0)

        self.driver.VSA_level('MAN')

        self.mock_vsa.write.assert_any_call(':INP:ATT:AUTO ON')
        self.mock_vsa.write.assert_any_call(':DISP:WIND:TRAC:Y:SCAL:RLEV 18.0')

    def test_VSA_load_writes_load_command(self):
        self.driver.VSA_load('state.dfl')
        self.mock_vsa.write.assert_called_once_with(':MMEM:LOAD:DEM:C1 "state.dfl"')

    def test_VSA_save_state_stores_file_and_launches_network(self):
        self.mock_vsa.query.side_effect = [
            'TEST_IDN',      # *IDN?
            'MU',            # :CONF:WLAN:RUC:EHTP?
            'PPDU_TYPE',     # :FETC:BURS:PPDU:TYPE?
            'MCS13',         # :CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:USER1:MCS?
            'RU4996',        # :CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:RUS?
            'OK'             # store state
        ]
        self.mock_vsa.queryInt.return_value = 80000000
        self.mock_vsa.s.getpeername.return_value = ('10.0.0.1', 5025)

        with patch('src.driver.WiFi_meas.os.system') as mock_system:
            self.driver.VSA_save_state()

        self.mock_vsa.query.assert_any_call('*IDN?')
        mock_system.assert_called_once_with('start \\\\10.0.0.1')

    def test_VSA_sweep_turns_off_continuous_and_triggers_single(self):
        self.driver.VSA_sweep()

        self.mock_vsa.write.assert_called_once_with('INIT:CONT OFF')
        self.mock_vsa.query.assert_called_once_with('INIT:IMM;*OPC?')

    def test_VSG_config_writes_generator_settings(self):
        self.driver.VSG_config()

        self.mock_vsg.write.assert_any_call(':SOUR1:BB:WLNN:BW BW320')
        self.mock_vsg.write.assert_any_call(':SOUR1:BB:WLNN:FBL1:TMOD EHT320')
        self.mock_vsg.write.assert_any_call(':OUTP1:STAT 1')
        self.mock_vsg.query.assert_any_call('*OPC?')

    def test_VSG_pwr_writes_power(self):
        self.driver.VSG_pwr(-12)
        self.mock_vsg.write.assert_called_once_with(':SOUR1:POW:POW -12')

    def test_VSG_save_state_handles_MU_direction(self):
        self.mock_vsg.query.side_effect = [
            'TEST_IDN', 'BW320', 'EHT320', 'MU', 'MCS13', 'RU4996', 'OK'
        ]
        self.mock_vsg.s.getpeername.return_value = ('10.0.0.2', 5025)

        with patch('src.driver.WiFi_meas.os.system') as mock_system:
            self.driver.VSG_save_state()

        mock_system.assert_called_once_with('start \\\\10.0.0.2\\user')
        self.assertTrue(self.mock_vsg.query.called)

    def test_VSx_freq_sets_both_instruments(self):
        self.driver.VSx_freq(2.4e9)

        self.mock_vsa.write.assert_called_once_with(':SENSE:FREQ:CENT 2400000000.0')
        self.mock_vsg.write.assert_called_once_with(':SOUR1:FREQ:CW 2400000000.0')


if __name__ == '__main__':
    unittest.main()
