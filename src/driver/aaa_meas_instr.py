from utils import method_timer, std_meas, std_config
from bench_config import bench
import os

class std_insr_driver():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)           # For AutoEVM
        self.VSG = bench().VSG_start()

    @method_timer
    def VSA_Config(self):
        '''VSA Config Before start of test suite'''
        self.VSA.query('*RST;*OPC?')                                    # Reset

    @method_timer
    def VSA_get_ACLR(self):
        pass

    def VSA_get_attn_reflvl(self):
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def VSA_get_chPwr(self):
        chPw = self.VSA.queryFloat(':FETC:CC1:SUMM:POW:AVER?')          # VSA CW Ch Pwr
        return chPw

    @method_timer
    def VSA_get_EVM(self):
        self.VSA.query('INIT:IMM;*OPC?')                            # Take a sweep
        EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        return EVM

    @method_timer
    def VSA_get_info(self):
        outStr = f'{freq:.3f}GHz_{ldir}_{dupl}_{chbw}_15kHz_{rbn}RB_{rbo}RBO_{cmod} {time}sec'
        print(outStr)
        return outStr

    @method_timer
    def VSA_level(self, method):
        '''# LEV:autolevel EVM:autoEVM'''
        if 'LEV' in method:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                      # Autolevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.get_VSA_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level

    def VSA_Load(self, file):
        '''VSA load state file'''


    def VSA_save_state(self):
        """VSA Save LTE State"""
        self.VSA.query(f'*IDN?')
        FSW_IP = self.VSA.s.getpeername()[0]            # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def VSA_sweep(self):
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    @method_timer
    def VSG_Config(self):
        '''VSG Config before start of test suite'''
        self.VSG.query('*OPC?')

    def VSG_pwr(self, pwr):
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def VSG_save_state(self):
        """VSG Save WLAN State"""

    def VSx_freq(self, freq):
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq


if __name__ == '__main__':
    林 = std_insr_driver()
    林.freq = 6e9           # Center Frequency, Hz
    std_config(林)
    std_meas(std_insr_driver())
