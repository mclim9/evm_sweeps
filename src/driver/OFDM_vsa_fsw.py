from driver.VSA_util import get_ch_power, get_ch_power_init
from helper.bench_config import BenchConfig
from helper.utils import method_timer
from driver.base_vsa import VSADriver
import os

class VSA_driver(VSADriver):
    def __init__(self, VSA=None):
        self.VSA = VSA or BenchConfig().VSA_start()
        self.VSA.s.settimeout(30)       # For AutoEVM
        self.sampleRate = 1728e6        # Sample Rate
        self.length  = 87               # Sequence Length
        self.cpl1 = 16                  # CP Length 1
        self.cpl2 = 16                  # CP Length 2
        self.dft = 1                    # DFT-s-OFDM on/off
        self.dft_ignore = 1             # DFT-s-OFDM Ignore don't care
        # self.xmsl = '/home/instrument/LEO_WV_example.xml'       # VSA-KM state filename
        self.xmsl = 'C:\R_S\instr\LEO_WV_example.xml'       # VSA-K96 state filename

    @method_timer
    def vsa_configure(self) -> None:
        """VSA Config Before start of test suite"""
        self.VSA.query('*RST;*OPC?')                            # Reset
        self.VSA.query(':SYST:DISP:UPD ON; *OPC?')              # Display on
        self.VSA.query(':INST:CRE:NEW OFDM, "OFDM VSA"; *OPC?') # Start OFDM VSA
        self.VSA.write(':INIT:CONT OFF')                        # Single Sweep
        self.VSA.write(f':MMEM:LOAD:CFGF "{self.xmsl}"')        # Load VSA state
        self.VSA.write(f':CONF:SYMB:NGU {self.cpl1}')           # CP Length 1
        self.VSA.write(f':CONF:SYMB:NSUF {self.cpl2}')          # CP Length 2
        self.VSA.write(f':TRAC:IQ:SRAT {self.sampleRate}')      # Sample Rate
        self.VSA.write(f':CONF:TPR {self.dft}')                 # DFT-s-OFDM
        self.VSA.write(f':CONF:TPR:IGN {self.dft_ignore}')      # Ignore Don't Care
        # self.VSA.write(':SENS1:FREQ:CENT 40000000000')
        self.VSA.write(f':SENS:DEM:FORM:NOFS {self.length}')    # Sample Length

        # Additional Settings
        self.VSA.write(':INIT:CONT OFF')                        # Single Sweep
        self.VSA.query(':LAY:ADD:WIND? "1",BEL,EVSC')           # EVM vs Sym vs Carr
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                    # Trigger External
        self.VSA.write(':SENS:SWE:TIME 0.000150')               # Capture Time
        get_ch_power_init(self.VSA)

    @method_timer
    def vsa_get_ACLR(self):
        return -9999

    def vsa_get_attn_ref(self):
        """Get VSA input atten and ref level.

        Returns:
            tuple: (attenuation, reference_level)
        """
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        prea = self.VSA.query('INP:GAIN:STAT?')                         # Preamp State
        return attn, refl, prea

    def vsa_get_ch_power(self) -> float:
        """Get VSA channel power from result summary"""
        # chPw = self.VSA.queryFloat(':FETC:SUMM:POW:AVER?')              # Result SUmmary
        chPw = get_ch_power(self.VSA)
        return chPw

    @method_timer
    def vsa_get_evm(self):
        """Takes a sweep then returns VSA EVM

        Returns:
            EVM(float) : EVM as defined by standard
        """
        try:
            self.vsa_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:SUMM:EVM:ALL:AVER?')       # VSA CW
        except:                                                         # noqa
            print('EVM 2nd Try')
            self.vsa_sweep()                                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:SUMM:EVM:ALL:AVER?')       # VSA CW
        return EVM

    def vsa_get_extra(self, extra=None) -> str:
        extra = extra.upper() if extra else ''
        if extra == 'IQNC':
            self.VSA.query(':SENS:ADJ:NCAN:AVER:STAT ON; *OPC?')            # IQNC On
            self.VSA.write(':SENS:ADJ:NCAN:AVER:COUN 10')                   # IQNC Averaging
        elif extra == 'XCORR':
            self.VSA.query(':SENS:IQ:XCOR:STAT ON; *OPC?')                  # XCorr On
        elif extra == 'ACLR_RMS':
            self.VSA.query(':SENS:WIND:DET1:FUNC RMS; *OPC?')               # RMS Detector
        elif extra == 'XCORR_RMS':
            self.VSA.query(':SENS:WIND:DET1:FUNC XRMS; *OPC?')              # XCORR RMS Detector
        extra = f'OFDM EVM {extra if extra else ""}'.strip()
        return extra

    def vsa_get_waveform_info(self) -> str:
        """VSA standard config detail string"""
        outStr = f'OFDM'
        self.Wavename = outStr
        print(outStr)
        return outStr

    def vsa_set_frequency(self, freq: float) -> None:
        """Configures both VSG & VSA to frequency"""
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq

    @method_timer
    def vsa_set_level(self, method='LEV') -> float:
        method = method.upper() if method else ''
        if 'LEV' in method:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                      # Autolevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            self.vsa_sweep()                                            # Take a sweep to update channel
            pwr = self.vsa_get_ch_power()
            # self.VSA.write(f'INP:RLEV {pwr + 4}')                     # Manually set ref level
            self.VSA.write(f'DISP:TRAC:Y:RLEV {pwr + 2}')               # Manually set ref level
        return 0.0

    def vsa_load(self, file):
        """Load VSA demodulation state from file.

        Args:
            file (str): Path to state file.
        """
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def vsa_save_state(self):
        """VSA Save 5G State"""
        self.VSA.query(f'*IDN?')
        self.Wavename = 'OFDM_FSx'
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
    print(林.vsa_get_ch_power())
