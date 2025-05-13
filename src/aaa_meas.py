from bench_config import bench

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
        pass

    @method_timer
    def get_info(self):
        freq = self.VSA.query(':SENS:FREQ:CENT?')                       # Center Frequency
        outStr = f'{freq:.3f}GHz_{ldir}_{dupl}_{chbw}_15kHz_{rbn}RB_{rbo}RBO_{cmod} {time}sec'
        print(outStr)
        return outStr

    def get_VSA_attn_reflvl(self):
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def get_VSA_chPwr(self):
        chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')     # VSA CW Ch Pwr
        return chPw

    @method_timer
    def set_VSA_init(self):
        pass

    def set_VSA_level(self, method='LEV'):
        pass

    @method_timer
    def get_VSA_sweep(self):
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    @method_timer
    def set_VSG_init(self):
        self.VSG.write(':SOUR1:CORR:OPT:EVM 1')                         # Optimize EVM
        self.VSG.query('*OPC?')

    def set_VSG_pwr(self, pwr):
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def set_VSx_freq(self, freq):
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq


if __name__ == '__main__':
    std_meas(option_functions())
