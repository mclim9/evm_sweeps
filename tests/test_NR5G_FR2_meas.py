import os
import sys
import unittest
from unittest.mock import MagicMock, patch

TEST_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, '..', 'src')))

from src.driver import NR5G_FR2_meas


class TestNR5G_FR2_Meas(unittest.TestCase):
    def setUp(self):
        self.bench_patcher = patch('src.driver.NR5G_FR2_meas.bench')
        self.mock_bench = self.bench_patcher.start()

        self.mock_vsa = MagicMock()
        self.mock_vsa.s = MagicMock()
        self.mock_vsg = MagicMock()

        self.mock_bench.return_value.VSA_start.return_value = self.mock_vsa
        self.mock_bench.return_value.VSG_start.return_value = self.mock_vsg

        self.driver = NR5G_FR2_meas.std_insr_driver()

    def tearDown(self):
        self.bench_patcher.stop()

    def test_init_starts_instruments_and_sets_timeout(self):
        self.mock_bench.return_value.VSA_start.assert_called_once()
        self.mock_bench.return_value.VSG_start.assert_called_once()
        self.mock_vsa.s.settimeout.assert_called_once_with(30)

    def test_VSA_config_sends_FR2_DL_commands(self):
        self.driver.ldir = 'DL'
        self.driver.VSA_config()

        self.mock_vsa.query.assert_any_call('*RST;*OPC?')
        self.mock_vsa.query.assert_any_call(':INST:CRE:NEW NR5G, "5G NR"; *OPC?')
        self.mock_vsa.write.assert_any_call(':TRIG:SEQ:SOUR EXT')

    def test_VSA_get_ACLR_returns_channel_power_and_aclr(self):
        self.driver.VSA_sweep = MagicMock()
        self.mock_vsa.query.side_effect = ['-9.5', '-42.0']

        result, _ = self.driver.VSA_get_ACLR()

        self.assertEqual(result, ('-9.5', '-42.0'))
        self.driver.VSA_sweep.assert_called_once()
        self.mock_vsa.write.assert_called_with(':CONF:NR5G:MEAS ACLR')

    def test_VSA_get_attn_reflvl_reads_attenuation_and_ref(self):
        self.mock_vsa.query.return_value = '20'
        self.mock_vsa.queryFloat.return_value = 3.14

        attn, refl = self.driver.VSA_get_attn_reflvl()

        self.assertEqual(attn, '20')
        self.assertEqual(refl, 3.14)
        self.mock_vsa.query.assert_called_once_with('INP:ATT?')
        self.mock_vsa.queryFloat.assert_called_once_with('DISP:TRAC:Y:SCAL:RLEV?')

    def test_VSA_get_chPwr_reads_channel_power(self):
        self.mock_vsa.queryFloat.return_value = 4.2

        chpw = self.driver.VSA_get_chPwr()

        self.assertEqual(chpw, 4.2)
        self.mock_vsa.queryFloat.assert_called_once_with(':FETC:CC1:ISRC:FRAM:SUMM:POW?')

    def test_VSA_get_EVM_runs_sweep_then_reads_evm(self):
        self.driver.VSA_sweep = MagicMock()
        self.mock_vsa.queryFloat.return_value = 1.23

        evm, elapsed = self.driver.VSA_get_EVM()

        self.assertEqual(evm, 1.23)
        self.assertIsInstance(elapsed, float)
        self.driver.VSA_sweep.assert_called_once()
        self.mock_vsa.queryFloat.assert_called_once_with(':FETC:CC1:SUMM:EVM:ALL:AVER?')

    def test_VSA_get_info_formats_expected_string(self):
        self.mock_vsa.query.side_effect = [
            '18000000000',
            'DL',
            'HIGH',
            'BW400',
            'SCS120',
            '264',
            'Q1K',
            'ON',
            '0.001',
            '1'
        ]

        info = self.driver.VSA_get_info()

        self.assertEqual(
            info,
            '18.0GHz_HIGH_DL_BW400_SCS120_264_Q1K_TPOff_PhaseCompON 0.001sec slots:1'
        )

    def test_VSA_level_EVM_and_LEV_use_query(self):
        self.driver.VSA_level('EVM')
        self.mock_vsa.query.assert_called_once_with(':SENS:ADJ:EVM;*OPC?')

        self.mock_vsa.query.reset_mock()
        self.driver.VSA_level('LEV')
        self.mock_vsa.query.assert_called_once_with(':SENS:ADJ:LEV;*OPC?')

    def test_VSA_level_manual_sets_manual_ref_level(self):
        self.driver.get_VSA_chPwr = MagicMock(return_value=7.0)

        self.driver.VSA_level('MAN')

        self.mock_vsa.write.assert_any_call(':INP:ATT:AUTO ON')
        self.mock_vsa.write.assert_any_call(':DISP:WIND:TRAC:Y:SCAL:RLEV 5.0')

    def test_VSA_load_writes_state_file_command(self):
        self.driver.VSA_load('state.dfl')
        self.mock_vsa.write.assert_called_once_with(':MMEM:LOAD:DEM:C1 "state.dfl"')

    def test_VSA_save_state_saves_allocation_and_launches_path(self):
        self.driver.Wavename = 'FR2_264'
        self.mock_vsa.query.side_effect = ['IDN', 'OK']
        self.mock_vsa.s.getpeername.return_value = ('192.168.0.20', 5025)

        with patch('src.driver.NR5G_FR2_meas.os.system') as mock_system:
            self.driver.VSA_save_state()

        self.mock_vsa.query.assert_any_call('*IDN?')
        self.mock_vsa.query.assert_any_call('MMEM:STOR:DEM "C:\\R_S\\instr\\FR2_264.allocation";*OPC?')
        mock_system.assert_called_once_with(r'start \\192.168.0.20\instr')

    def test_VSA_sweep_writes_and_queries_single_sweep(self):
        self.driver.VSA_sweep()

        self.mock_vsa.write.assert_called_once_with('INIT:CONT OFF')
        self.mock_vsa.query.assert_called_once_with('INIT:IMM;*OPC?')

    def test_VSG_config_writes_FR2_configuration(self):
        self.driver.ldir = 'DL'
        self.driver.VSG_config()

        self.mock_vsg.write.assert_any_call(':SOUR1:BB:NR5G:LINK DL')
        self.mock_vsg.write.assert_any_call(':SOUR1:BB:NR5G:QCKS:GEN:CARD FR2_1')
        self.mock_vsg.query.assert_any_call(':SOUR1:CORR:OPT:EVM 1;*OPC?')

    def test_VSG_pwr_writes_power_level(self):
        self.driver.VSG_pwr(-18)
        self.mock_vsg.write.assert_called_once_with(':SOUR1:POW:POW -18')

    def test_VSG_save_state_handling_UP_direction(self):
        self.mock_vsg.query.side_effect = [
            'IDN', 'BAND', 'UP', 'BW400', 'SCS120', 'Q1K', '264', 'OK'
        ]
        self.mock_vsg.s.getpeername.return_value = ('192.168.0.21', 5025)

        with patch('src.driver.NR5G_FR2_meas.os.system') as mock_system:
            self.driver.VSG_save_state()

        self.assertTrue(self.mock_vsg.query.called)
        mock_system.assert_called_once_with(r'start \\192.168.0.21\user')

    def test_VSx_freq_sets_both_vsa_and_vsg(self):
        self.driver.VSx_freq(26.5e9)

        self.mock_vsa.write.assert_called_once_with(':SENSE:FREQ:CENT 26500000000.0')
        self.mock_vsg.write.assert_called_once_with(':SOUR1:FREQ:CW 26500000000.0')


if __name__ == '__main__':
    unittest.main()
