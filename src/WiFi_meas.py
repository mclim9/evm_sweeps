from bench_config import bench
from utils import method_timer, std_meas

class option_functions():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)           # For AutoEVM
        self.VSG = bench().VSG_start()

    @method_timer
    def get_ACLR(self):
        pass

    @method_timer
    def get_EVM(self):
        EVM = self.VSA.query(':FETC:BURS:EVM:DATA:AVER?').split(',')    # EVM
        try:
            EVM = float(EVM[0])
        except:                                                         # noqa
            EVM = 999
        return EVM

    def get_info(self):
        freq = self.VSG.query(':SOUR1:FREQ:CW?')                        # Center Frequency
        freq = int(freq) / 1e9
        Std  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:TMOD?')              # Standard
        BW   = self.VSG.query(':SOUR1:BB:WLNN:BW?')                     # Bandwidth
        MCS  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:MCS?')         # MCS
        Data = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:DATA:LENG?')   # PPDU Length
        outStr = f'{freq}GHz_{Std}_{BW}_{MCS}_{Data}A-MPDU'
        print(outStr)
        return outStr

    def get_VSA_attn_reflvl(self):
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def get_VSA_chPwr(self):
        chPw = 999
        # chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')   # VSA CW Ch Pwr
        return chPw

    @method_timer
    def set_VSA_init(self):
        self.VSA.write('INIT:CONT OFF')                                 # Single Sweep
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                            # Trigger External
        self.VSA.write(':SENS:DEM:TXAR OFF')                            # Power Interval Search

    @method_timer
    def set_VSA_level(self, method):
        '''# LEV:autolevel EVM:autoEVM'''
        if 'LEV' in method:
            self.VSA.query(f':CONF:POW:AUTO ONCE;*OPC?')                # AutoLevel
        elif 'EVM' in method:
            self.VSA.query(f':CONF:POW:AUTO ONCE;*OPC?')                # AutoLevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.get_VSA_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level

    @method_timer
    def get_VSA_sweep(self):
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    @method_timer
    def set_VSG_init(self):
        self.VSG.write(':SOUR1:CORR:OPT:EVM 1')                         # Optimize EVM
        self.VSG.write(':SOUR1:BB:EUTR:TRIG:OUTP1:MODE REST')           # Maker Mode Arb Restart
        self.VSG.query('*OPC?')

    def set_VSG_pwr(self, pwr):
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def set_VSx_freq(self, freq):
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq


if __name__ == '__main__':
    std_meas(option_functions())
