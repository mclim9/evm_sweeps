from bench_config import bench

class option_functions():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)           # For AutoEVM
        self.VSG = bench().VSG_start()

    def get_ACLR(self):
        pass

    def get_EVM(self):
        pass

    def get_info(self):
        pass
        return outStr

    def get_VSA_attn_reflvl(self):
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def get_VSA_chPwr(self):
        chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')     # VSA CW Ch Pwr
        return chPw

    def set_VSA_init(self):
        pass

    def set_VSA_level(self, method='LEV'):
        pass

    def get_VSA_sweep(self):
        pass

    def set_VSG_init(self):
        pass

    def set_VSG_pwr(self, pwr):
        pass

    def set_VSx_freq(self, freq):
        pass


if __name__ == '__main__':
    林 = option_functions()
    林.get_info()
    林.set_VSA_init()
    林.set_VSG_init()
    EVMM = 林.get_EVM()
    ACLR = 林.get_ACLR()
    chPw = 林.get_VSA_chPwr()
    print(f'EVM:{EVMM:.2f} CH_Pwr:{chPw:.2f} ACLR:{ACLR}')
