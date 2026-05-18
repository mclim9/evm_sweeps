import os
import sys

# Add src directory to path for imports when running standalone
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsa import VSADriver
from tkinter import Tk, messagebox as tkMessageBox

class VSA_driver(VSADriver):
    def __init__(self, VSA=None):
        self.VSA = VSA or BenchConfig().VSA_start()
        self.VSA.s.settimeout(30)       # For AutoEVM
        self.base_path = "/home/instrument"

    @method_timer
    def vsa_configure(self) -> None:
        """VSA Config Before start of test suite"""
        self.VSA.query('*RST;*OPC?')                            # Reset
        self.VSA.query(':SYST:DISP:UPD ON; *OPC?')              # Display on
        self.VSA.query(':INST:CRE:NEW AMPL, "Amplifier"; *OPC?') # Start Amplifier mode
        wv_file = "WLAN_802.11ax_160_mcs13_burst0.180ms_duty0.5.wv"
        self.VSA.write(f':CONF:REFS:CWF:FPAT "{self.base_path}/{wv_file}"')                    # Set Gen Func to CW
        # self.VSA.write(':CONF:GEN:IPC:ADDR "192.168.8.20"')     # SMW IP
        # self.VSA.query(':CONF:GEN:CONN:STAT ON;*OPC?')          # Wait to connect
        tkMessageBox.showinfo(title="FSWX KM118", message="Verify waveform loaded")

        # Additional Settings
        self.VSA.write(':CONF:EVM:UNIT DB')                     # EVM Unit to dB
        self.VSA.write(':TRIG:SEQ:SOUR IMM')                    # Trigger External
        # self.VSA.write(':SENS:SWE:TIME 0.015')                # Capture Time

    @method_timer
    def vsa_get_ACLR(self):
        chPwr = self.VSA.query(':FETC:POW:OUTP:CURR:RES?')              # Channel Power
        ACLRV = 'none'
        print(f'{chPwr} {ACLRV}')
        return chPwr, ACLRV

    def vsa_get_attn_ref(self):
        """Get VSA input atten and ref level.

        Returns:
            tuple: (attenuation, reference_level)
        """
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('INP:RLEV?')                         # Ref Level
        prea = self.VSA.query('INP:GAIN:STAT?')                         # Preamp Auto
        return attn, refl

    def vsa_get_ch_power(self) -> float:
        chPw = self.VSA.queryFloat(':FETC:POW:OUTP:CURR:RES?')          # VSA CW Ch Pwr
        return chPw

    @method_timer
    def vsa_get_evm(self):
        try:
            self.vsa_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:MACC:REVM:CURR:RES?')      # VSA CW
        except:                                                         # noqa
            print('EVM 2nd Try')
            self.vsa_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:MACC:REVM:CURR:RES?')      # VSA CW
        return EVM

    def vsa_get_extra(self) -> str:
        extra = 'none'  # 'XCORR' or 'IQNC'
        if extra == 'IQNC':
            self.VSA.query(':SENS:ADJ:NCAN:AVER:STAT ON; *OPC?')        # IQNC On
            self.VSA.write(':SENS:ADJ:NCAN:AVER:COUN 10')               # IQNC Averaging
        elif extra == 'XCORR':
            self.VSA.query(':SENS:IQ:XCOR:STAT ON; *OPC?')              # XCorr On
        extra = f'K18 EVM {extra}'
        return extra

    def vsa_get_waveform_info(self) -> str:
        """VSA standard config detail string

        Returns:
            outStr(str): Formatted string with configuration details.
        """
        freq = self.VSA.query(':SENS:FREQ:CENT?')                       # Center Frequency
        freq = int(freq) / 1e9

        outStr = f'{freq}GHz_K18'
        self.Wavename = outStr
        print(outStr)
        return outStr

    def vsa_set_frequency(self, freq: float) -> None:
        self.VSA.write(f':SENS1:FREQ:CENT {freq}')                      # Ana CC Center Freq

    @method_timer
    def vsa_set_level(self, method='LEV') -> float:
        if 'LEV' in method:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                      # Autolevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            self.vsa_sweep()                                            # Take a sweep to update channel
            pwr = self.vsa_get_ch_power()
            self.VSA.write(f'INP:RLEV {pwr + 2}')                       # Manually set ref level
        return 0.0

    def vsa_load(self, file):
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def vsa_save_state(self):
        """VSA Save 5G State"""
        self.VSA.query(f'*IDN?')
        self.VSA.query(f'MMEM:STOR:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        # HST_IP = self.VSA.s.getsockname()[0]                  # Host PC
        FSW_IP = self.VSA.s.getpeername()[0]                    # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def vsa_sweep(self):
        """VSA take a single sweep"""
        self.VSA.write('INIT:CONT OFF')
        self.VSA.query('INIT:IMM;*OPC?')

if __name__ == '__main__':
    林 = VSA_driver(BenchConfig().VSA_start())
    林.vsa_configure()
    林.vsa_set_frequency(6e9)
    林.vsa_sweep()
    林.vsa_set_level('MAN')
    林.vsa_get_evm()
