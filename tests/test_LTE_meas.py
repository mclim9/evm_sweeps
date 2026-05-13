import os
import sys
import unittest
from unittest.mock import MagicMock, patch

TEST_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '..', 'src')))

from src.driver import LTE_meas


class TestLTE_Meas(unittest.TestCase):
    def setUp(self):
        self.bench_patcher = patch('src.driver.LTE_meas.bench')
        self.mock_bench = self.bench_patcher.start()

        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()
        self.mock_vsg = MagicMock()

        self.mock_bench.return_value.VSA_start.return_value = self.mock_vsa
        self.mock_bench.return_value.VSG_start.return_value = self.mock_vsg

        self.driver = LTE_meas.std_insr_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_starts_instruments_and_sets_timeout(self):
        self.mock_bench.return_value.VSA_start.assert_called_once()
        self.mock_bench.return_value.VSG_start.assert_called_once()
        self.mock_vsa.s.settimeout.assert_called_once_with(30)

    def test_VSA_config_sends_LTE_setup_commands(self):
        self.driver.VSA_config()

        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':INIT:IMM;*OPC?')
        self.mock_vsa.write.assert_any_call(':TRIG:SEQ:SOUR EXT;*WAI')
        self.mock_vsa.write.assert_any_call(':CONF:LTE:UL:CC:SUBF0:ALL:MOD QAM256')

    def test_VSA_get_ACLR_returns_channel_power_and_ACLR(self):
        self.driver.VSA_sweep = MagicMock()
        self.mock_vsa.queryFloat.side_effect = [-10.5, -45.8]

        result, _ = self.driver.VSA_get_ACLR()

        self.assertEqual(result, (-10.5, -45.8))
        self.driver.VSA_sweep.assert_called_once()
        self.mock_vsa.write.assert_called_with(':CONF:LTE:MEAS ACLR')

    def test_VSA_get_attn_reflvl_returns_attn_and_ref_level(self):
        self.mock_vsa.query.return_value = '12'
        self.mock_vsa.queryFloat.return_value = 1.2

        attn, refl = self.driver.VSA_get_attn_reflvl()

        self.assertEqual(attn, '12')
        self.assertEqual(refl, 1.2)
        self.mock_vsa.query.assert_called_once_with('INP:ATT?')
        self.mock_vsa.queryFloat.assert_called_once_with('DISP:TRAC:Y:SCAL:RLEV?')

    def test_VSA_get_chPwr_returns_channel_power(self):
        self.mock_vsa.queryFloat.return_value = -15.2

        chPwr = self.driver.VSA_get_chPwr()

        self.assertEqual(chPwr, -15.2)
        self.mock_vsa.queryFloat.assert_called_once_with(':FETC:CC1:SUMM:POW:AVER?')

    def test_VSA_get_EVM_returns_value_and_time(self):
        self.mock_vsa.queryFloat.return_value = 3.1

        evm, elapsed = self.driver.VSA_get_EVM()

        self.assertEqual(evm, 3.1)
        self.assertIsInstance(elapsed, float)
        self.mock_vsa.query.assert_called_once_with('INIT:IMM;*OPC?')
        self.mock_vsa.queryFloat.assert_called_once_with(':FETC:CC1:SUMM:EVM:ALL:AVER?')

    def test_VSA_get_info_formats_string(self):
        self.mock_vsa.query.side_effect = [
            '6000000000',  # freq
            'UL',          # ldir
            'FDD',         # dupl
            'BW5_00',      # chbw
            'QAM256',      # cmod
            '24',          # rbn
            '0',           # rbo
        ]

        info, _ = self.driver.VSA_get_info()

        self.assertEqual(info, '6.000GHz_UL_FDD_BW5_00_15kHz_24RB_0RBO_QAM256 0sec')

    def test_VSA_level_autolevel_uses_query(self):
        self.driver.VSA_level('LEV')
        self.mock_vsa.query.assert_called_once_with(':SENS:ADJ:LEV;*OPC?')

    def test_VSA_level_manual_sets_ref_level(self):
        self.driver.get_VSA_chPwr = MagicMock(return_value=20.0)

        self.driver.VSA_level('MAN')

        self.mock_vsa.write.assert_any_call(':INP:ATT:AUTO ON')
        self.mock_vsa.write.assert_any_call(':DISP:WIND:TRAC:Y:SCAL:RLEV 18.0')

    def test_VSA_Load_writes_load_command(self):
        self.driver.VSA_Load('state.dfl')
        self.mock_vsa.write.assert_called_once_with(':MMEM:LOAD:DEM:C1 "state.dfl"')

    def test_VSA_save_state_stores_file_and_launches_network(self):
        self.mock_vsa.query.side_effect = [
            'TEST_IDN', 'UL', 'FDD', 'BW5_00', '24', '0', 'QAM256', 'OK'
        ]
        self.mock_vsa.s.getpeername.return_value = ('10.0.0.1', 5025)

        with patch('src.driver.LTE_meas.os.system') as mock_system:
            self.driver.VSA_save_state()

        self.mock_vsa.query.assert_any_call('*IDN?')
        mock_system.assert_called_once_with(r'start \\10.0.0.1\instr')

    def test_VSA_sweep_turns_off_continuous_and_triggers_single(self):
        self.driver.VSA_sweep()

        self.mock_vsa.write.assert_called_once_with('INIT:CONT OFF')
        self.mock_vsa.query.assert_called_once_with('INIT:IMM;*OPC?')

    def test_VSG_config_writes_generator_settings(self):
        self.driver.VSG_config()

        self.mock_vsg.write.assert_any_call(':SOUR1:BB:EUTR:STDM LTE')
        self.mock_vsg.write.assert_any_call(':OUTP1:STAT 1')
        self.mock_vsg.query.assert_any_call('*OPC?')

    def test_VSG_pwr_writes_power(self):
        self.driver.VSG_pwr(-12)
        self.mock_vsg.write.assert_called_once_with(':SOUR1:POW:POW -12')

    def test_VSG_save_state_handles_UP_direction(self):
        self.mock_vsg.query.side_effect = [
            'TEST_IDN', 'UP', 'FDD', 'QAM256', '24', '0', 'BW5_00', 'OK'
        ]
        self.mock_vsg.s.getpeername.return_value = ('10.0.0.2', 5025)

        with patch('src.driver.LTE_meas.os.system') as mock_system:
            self.driver.VSG_save_state()

        mock_system.assert_called_once_with(r'start \\10.0.0.2\user')
        self.assertTrue(self.mock_vsg.query.called)

    def test_VSx_freq_sets_both_instruments(self):
        self.driver.VSx_freq(3.2e9)

        self.mock_vsa.write.assert_called_once_with(':SENSE:FREQ:CENT 3200000000.0')
        self.mock_vsg.write.assert_called_once_with(':SOUR1:FREQ:CW 3200000000.0')


if __name__ == '__main__':
    unittest.main()
