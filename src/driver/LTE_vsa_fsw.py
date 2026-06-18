from helper.bench_config import BenchConfig
from helper.utils import method_timer
from driver.base_vsa import VSADriver
from typing import Tuple
import os

class VSA_driver(VSADriver):
    def __init__(self, VSA=None):
        self.VSA = VSA or BenchConfig().VSA_start()
        self.VSA.s.settimeout(30)                   # For AutoEVM
        self.bw = 5                                 # Default Ch BW, MHz
        self.rbc = 24                               # Default Num RB
        self.rbo = 0                                # Default RB Offset
        self.Wavename = 'default'

    @method_timer
    def vsa_configure(self) -> None:
        """VSA Config Before start of test suite"""
        self.VSA.query('*RST;*OPC?')                                    # Reset
        self.VSA.query(f':INST:CRE:NEW LTE, "LTE";*OPC?')               # Opens LTE Mode
        self.VSA.write(f':TRIG:SEQ:SOUR EXT;*WAI')                      # Trigger External
        self.VSA.write(f':INIT:CONT ON;*WAI')                           # Continuous sweep
        self.VSA.write(f':CONF:LTE:DUPL FDD;*WAI')                      # Duplexing: FDD
        self.VSA.write(f':CONF:LTE:LDIR UL;*WAI')                       # Link direction: UL
        self.VSA.write(f':CONF:LTE:UL:CC:BW BW{self.bw}_00;*WAI')       # Channel BW
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:RBC {self.rbc}')    # Num RB
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:rboF {self.rbo}')   # RB Offset
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:MOD QAM256')         # Modulation
        self.VSA.write(f':SENS:SWE:TIME 0.00201;*WAI')                  # Sweep Time
        self.VSA.write(f':SENS:LTE:FRAM:SSUB ON;*WAI')                  # Single Subframe Mode

        self.VSA.write(f':SYST:DISP:UPD ON')                            # Display On
        self.VSA.write('INIT:CONT OFF')                                 # Single Sweep
        self.VSA.query(f':INIT:IMM;*OPC?')                              # Run Single

    def vsa_get_attn_ref(self) -> Tuple[str, float]:
        """Get VSA input atten and ref level."""
        attn = self.VSA.query('INP:ATT?')
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')
        prea = self.VSA.query('INP:GAIN:STAT?')                         # Preamp State
        return attn, refl, prea

    @method_timer
    def vsa_get_ACLR(self) -> Tuple[float, float]:
        """Get VSA ACLR."""
        self.VSA.write(':CONF:LTE:MEAS ACLR')
        self.vsa_sweep()
        chPwr = self.VSA.queryFloat(':CALC:MARK:FUNC:POW:RES? CPOW')
        ACLRV = self.VSA.queryFloat(':CALC:MARK:FUNC:POW:RES? ACP')
        return chPwr, ACLRV

    def vsa_get_ch_power(self) -> float:
        """Get VSA Channel Power"""
        chPwr = self.VSA.queryFloat(':FETC:CC1:SUMM:POW:AVER?')
        return chPwr

    @method_timer
    def vsa_get_evm(self) -> float:
        """Takes a sweep then returns VSA EVM"""
        try:
            self.vsa_sweep()
            evm = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')
        except Exception:
            self.vsa_sweep()
            evm = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')
        return evm

    def vsa_get_extra(self) -> str:
        return 'FSW-LTE'

    def vsa_get_waveform_info(self) -> str:
        """Construct LTE configuration detail string."""
        freq = self.VSA.queryInt(':SENS:FREQ:CENT?') / 1e9
        ldir = self.VSA.query(':CONF:LTE:LDIR?')
        dupl = self.VSA.query(':CONF:LTE:DUPL?')
        ldir = "UL" if ldir == "UL" else "DL"
        chbw = self.VSA.query(f':CONF:LTE:{ldir}:CC:BW?')
        cmod = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:MOD?')
        rbn  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBC?')
        rbo  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBOF?')

        outStr = f'{freq:.3f}GHz_{ldir}_{dupl}_{chbw}_15kHz_{rbn}RB_{rbo}RBO_{cmod}'
        self.Wavename = outStr
        return outStr

    def vsa_save_state(self) -> None:
        """VSA Save LTE State"""
        self.VSA.query(f'*IDN?')
        info = self.vsa_get_waveform_info()
        self.VSA.query(f'MMEM:STOR:CC:DEM "C:\\R_S\\instr\\{info}.allocation";*OPC?')
        FSW_IP = self.VSA.s.getpeername()[0]
        os.system(f'start \\\\{FSW_IP}\\instr')

    def vsa_set_frequency(self, freq: float) -> None:
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')

    @method_timer
    def vsa_set_level(self, mode: str) -> float:
        if 'LEV' in mode:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')
            pwr = self.vsa_get_ch_power()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')
        return 0.0

    @method_timer
    def vsa_sweep(self) -> None:
        """VSA take a single sweep"""
        self.VSA.write('INIT:CONT OFF')
        self.VSA.query('INIT:IMM;*OPC?')

if __name__ == '__main__':
    driver = VSA_driver()
    driver.vsa_configure()
    print(driver.vsa_get_waveform_info())
    print(f"EVM: {driver.vsa_get_evm()}")
