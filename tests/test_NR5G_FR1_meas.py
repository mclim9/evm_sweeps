import os
import sys
import unittest
from src.driver import NR5G_FR1_meas
from unittest.mock import MagicMock, patch

TEST_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '..', 'src')))



class TestNR5G_FR1_Meas(unittest.TestCase):
    def setUp(self):
        self.bench_patcher = patch('src.driver.NR5G_FR1_meas.bench')
        self.mock_bench = self.bench_patcher.start()

        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()
        self.mock_vsg = MagicMock()

        self.mock_bench.return_value.VSA_start.return_value = self.mock_vsa
        self.mock_bench.return_value.VSG_start.return_value = self.mock_vsg

        self.driver = NR5G_FR1_meas.std_insr_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_starts_instruments_and_sets_timeout(self):
        self.mock_bench.return_value.VSA_start.assert_called_once()
        self.mock_bench.return_value.VSG_start.assert_called_once()
        self.mock_vsa.s.settimeout.assert_called_once_with(30)

    def test_VSA_config_sends_required_commands(self):
        self.driver.VSA_config()

        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':SYST:DISP:UPD ON; *OPC?')
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW NR5G, "5G NR"; *OPC?')
        self.mock_vsa.write.assert_any_call(':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBC 273')
        self.mock_vsa.write.assert_any_call(':DISP:WIND2:TABL:ITEM UCCH,ON')
        self.mock_vsa.write.assert_any_call(':TRIG:SEQ:SOUR IMM')

    def test_VSA_get_ACLR_returns_power_and_aclr(self):
        self.driver.VSA_sweep = MagicMock()
        self.mock_vsa.query.side_effect = ['-5.0', '-55.0']

        result, _ = self.driver.VSA_get_ACLR()

        self.assertEqual(result, ('-5.0', '-55.0'))
        self.driver.VSA_sweep.assert_called_once()
        self.mock_vsa.write.assert_called_with(':CONF:NR5G:MEAS ACLR')

    def test_VSA_get_attn_reflvl_returns_values(self):
        self.mock_vsa.query.return_value = '15'
        self.mock_vsa.queryFloat.return_value = 0.5

        attn, refl = self.driver.VSA_get_attn_reflvl()

        self.assertEqual(attn, '15')
        self.assertEqual(refl, 0.5)
        self.mock_vsa.query.assert_called_once_with('INP:ATT?')
        self.mock_vsa.queryFloat.assert_called_once_with('DISP:TRAC:Y:SCAL:RLEV?')

    def test_VSA_get_chPwr_returns_channel_power(self):
        self.mock_vsa.queryFloat.return_value = 1.23

        chpw = self.driver.VSA_get_chPwr()

        self.assertEqual(chpw, 1.23)
        self.mock_vsa.queryFloat.assert_called_once_with(':FETC:CC1:ISRC:FRAM:SUMM:POW?')

    def test_VSA_get_EVM_returns_value_and_time(self):
        self.driver.VSA_sweep = MagicMock()
        self.mock_vsa.queryFloat.return_value = 2.7

        evm, elapsed = self.driver.VSA_get_EVM()

        self.assertEqual(evm, 2.7)
        self.assertIsInstance(elapsed, float)
        self.driver.VSA_sweep.assert_called_once()
        self.mock_vsa.queryFloat.assert_called_once_with(':FETC:CC1:SUMM:EVM:ALL:AVER?')

    def test_VSA_get_info_formats_expected_string(self):
        self.mock_vsa.query.side_effect = [
            '6000000000',  # freq
            'UL',          # ldir
            'FR1GT3',      # frng
            'BW100',       # chbw
            'SCS30',       # bscs
            '273',         # bwrb
            'Q1K',         # cmod
            'OFF',         # tpre
            'ON',          # phas
            '0.015',       # time
            '1'            # nslt
        ]

        info = self.driver.VSA_get_info()

        self.assertEqual(
            info,
            '6.0GHz_FR1GT3_UL_BW100_SCS30_273_Q1K_TPOFF_PhaseCompON 0.015sec slots:1'
        )

    def test_VSA_level_autolevel_calls_query(self):
        self.driver.VSA_level('LEV')
        self.mock_vsa.query.assert_called_once_with(':SENS:ADJ:LEV;*OPC?')

    def test_VSA_level_autoEVM_calls_query(self):
        self.driver.VSA_level('EVM')
        self.mock_vsa.query.assert_called_with(':SENS:ADJ:EVM;*OPC?')

    def test_VSA_level_manual_uses_manual_ref(self):
        self.driver.get_VSA_chPwr = MagicMock(return_value=10.0)

        self.driver.VSA_level('MAN')

        self.mock_vsa.write.assert_any_call(':INP:ATT:AUTO ON')
        self.mock_vsa.write.assert_any_call(':DISP:WIND:TRAC:Y:SCAL:RLEV 8.0')

    def test_VSA_load_writes_load_command(self):
        self.driver.VSA_load('state.dfl')
        self.mock_vsa.write.assert_called_once_with(':MMEM:LOAD:DEM:C1 "state.dfl"')

    def test_VSA_save_state_stores_file_and_launches_network(self):
        self.driver.Wavename = 'NR5G_273'
        self.mock_vsa.query.side_effect = ['IDN', 'OK']
        self.mock_vsa.s.getpeername.return_value = ('192.168.0.10', 5025)

        with patch('src.driver.NR5G_FR1_meas.os.system') as mock_system:
            self.driver.VSA_save_state()

        self.mock_vsa.query.assert_any_call('*IDN?')
        self.mock_vsa.query.assert_any_call('MMEM:STOR:DEM "C:\\R_S\\instr\\NR5G_273.allocation";*OPC?')
        mock_system.assert_called_once_with(r'start \\192.168.0.10\instr')

    def test_VSA_sweep_performs_single_sweep(self):
        self.driver.VSA_sweep()

        self.mock_vsa.write.assert_called_once_with('INIT:CONT OFF')
        self.mock_vsa.query.assert_called_once_with('INIT:IMM;*OPC?')

    def test_VSG_config_writes_quick_settings(self):
        self.driver.VSG_config()

        self.mock_vsg.write.assert_any_call(':SOUR1:BB:NR5G:LINK UP')
        self.mock_vsg.write.assert_any_call(':SOUR1:BB:NR5G:QCKS:GEN:ES:MOD QAM1024')
        self.mock_vsg.query.assert_any_call(':SOUR1:CORR:OPT:EVM 1;*OPC?')

    def test_VSG_pwr_writes_power_command(self):
        self.driver.VSG_pwr(-20)
        self.mock_vsg.write.assert_called_once_with(':SOUR1:POW:POW -20')

    def test_VSG_save_state_handles_up_direction(self):
        self.mock_vsg.query.side_effect = [
            'IDN', 'BAND', 'UP', 'BW100', 'SCS30', 'Q1K', '273', 'OK'
        ]
        self.mock_vsg.s.getpeername.return_value = ('192.168.0.11', 5025)

        with patch('src.driver.NR5G_FR1_meas.os.system') as mock_system:
            self.driver.VSG_save_state()

        self.assertTrue(self.mock_vsg.query.called)
        mock_system.assert_called_once_with(r'start \\192.168.0.11\user')

    def test_VSx_freq_sets_both_instruments(self):
        self.driver.VSx_freq(3.4e9)

        self.mock_vsa.write.assert_called_once_with(':SENSE:FREQ:CENT 3400000000.0')
        self.mock_vsg.write.assert_called_once_with(':SOUR1:FREQ:CW 3400000000.0')


if __name__ == '__main__':
    unittest.main()
