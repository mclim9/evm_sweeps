from bench_config import bench

class option_functions():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSG = bench().VSG_start()

    def get_ACLR(self):
        pass

    def get_EVM(self):
        EVM = self.VSA.query(':FETC:BURS:EVM:DATA:AVER?').split(',')    # EVM
        try:
            EVM = float(EVM[0])
        except:
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

    def get_VSA_chPwr(self):
        chPw = 999
        # chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')     # VSA CW Ch Pwr
        return chPw

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

    def set_freq(self, freq):
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq

    def set_VSA_init(self):
        self.VSA.write('INIT:CONT OFF')                                 # Single Sweep
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                            # Trigger External
        self.VSA.write(':SENS:DEM:TXAR OFF')                            # Power Interval Search

    def set_VSG_init(self):
        self.VSG.write(':SOUR1:CORR:OPT:EVM 1')                         # Optimize EVM
        self.VSG.write(':SOUR1:BB:WLNN:TRIG:OUTP1:MODE REST')           # Marker Mode Arb Restart


if __name__ == '__main__':
    林 = option_functions()
    林.get_info()
