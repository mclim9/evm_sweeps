from bench_config import bench

class option_functions():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)           # For AutoEVM
        self.VSG = bench().VSG_start()

    def get_ACLR(self):
        pass

    def get_EVM(self):
        try:
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        except:
            self.VSA.query('INIT:IMM;*OPC?')
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        return EVM

    def get_info(self):
        freq = self.VSA.query(':SENS:FREQ:CENT?')                       # Center Frequency
        freq = int(freq) / 1e9
        ldir = self.VSA.query(':CONF:LTE:LDIR?')                        # link direction
        dupl = self.VSA.query(':CONF:LTE:DUPL?')                        # duplex mode
        ldir = "UL" if ldir == "UL" else "DL"
        chbw = self.VSA.query(f':CONF:LTE:{ldir}:CC:BW?')
        cmod = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:MOD?')
        rbn  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBC?')
        rbo  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBOF?')
        # time = self.VSA.query(':SENS:SWE:TIME?')                      # measure time
        time = 0

        outStr = f'{freq:.3f}GHz_{ldir}_{dupl}_{chbw}_15kHz_{rbn}RB_{rbo}RBO_{cmod} {time}sec'
        print(outStr)
        return outStr

    def get_VSA_attn_reflvl(self):
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def get_VSA_chPwr(self):
        chPw = self.VSA.queryFloat(':FETC:CC1:SUMM:POW:AVER?')          # VSA CW Ch Pwr
        return chPw

    def set_VSA_init(self):
        self.VSA.write('INIT:CONT OFF')                                 # Single Sweep
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                            # Trigger External
        # self.VSA.write(':SENS:LTE:FRAM:COUN:AUTO OFF')                # Frame count off
        # self.VSA.write(':SENS:LTE:FRAM:COUN 1')                       # Single frame
        # self.VSA.write(':SENS:SWE:TIME 0.002')                        # Capture Time
        self.VSA.write(':SENS:LTE:FRAM:SSUB ON')                        # Single Subframe Mode

    def set_VSA_level(self, method='LEV'):
        '''# LEV:autolevel'''
        self.VSA.tick()
        if 'LEV' in method:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                      # Autolevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.get_VSA_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level
        return self.VSA.tock()

    def get_VSA_sweep(self):
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    def set_VSG_init(self):
        self.VSG.write(':SOUR1:CORR:OPT:EVM 1')                         # Optimize EVM
        self.VSG.write(':SOUR1:BB:EUTR:TRIG:OUTP1:MODE REST')           # Maker Mode Arb Restart

    def set_VSG_pwr(self, pwr):
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def set_VSx_freq(self, freq):
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq


if __name__ == '__main__':
    林 = option_functions()
    林.get_info()
    林.set_VSA_init()
    林.set_VSG_init()
    EVMM = 林.get_EVM()
    ACLR = 林.get_ACLR()
    chPw = 林.get_VSA_chPwr()
    print(f'EVM:{EVMM:.2f} CH_Pwr:{chPw:.2f} ACLR:{ACLR}')
