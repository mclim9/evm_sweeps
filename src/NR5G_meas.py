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
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')       # VSA CW
        except:
            self.VSA.query('INIT:IMM;*OPC?')
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')       # VSA CW
        return EVM

    def get_info(self):
        freq = self.VSA.query(':SENS:FREQ:CENT?')                       # Center Frequency
        freq = int(freq) / 1e9
        ldir = self.VSA.query(':CONF:NR5G:LDIR?')                       # LinkDir
        frng = self.VSA.query(f':CONF:{ldir}:DFR?')                     # Freq Range
        chbw = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:BW?')             # Ch Width
        bscs = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:FRAM1:BWP0:SSP?') # BWP Sub Carr Spacing
        bwrb = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:FRAM1:BWP0:RBC?') # BWP RB Allocation
        cmod = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:FRAM1:BWP0:SLOT0:ALL0:MOD?')    # channel Modulation
        if ldir == 'UL':
            tpre = self.VSA.query(f':CONF:NR5G:UL:CC1:TPR?')            # Trans Precoding State
        else:
            tpre = 'Off'
        phas = self.VSA.query(f':CONF:NR5G:{ldir}:CC1:RFUC:STAT?')      # Phase comp state
        time = self.VSA.query(':SENS:SWE:TIME?')                        # measure time
        nslt = self.VSA.query(':SENS:NR5G:FRAM:SLOT?')                  # number of slots

        outStr = f'{freq}GHz_{frng}_{ldir}_{chbw}_{bscs}_{bwrb}_{cmod}_TP{tpre}_PhaseComp{phas} {time}sec slots:{nslt}'
        print(outStr)
        return outStr

    def get_VSA_chPwr(self):
        chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')     # VSA CW Ch Pwr
        return chPw

    def set_VSA_level(self, method):
        '''# LEV:autolevel EVM:autoEVM'''
        if 'EVM' in method:
            self.VSA.query(f':SENS:ADJ:EVM;*OPC?')                      # AutoEVM
        elif 'LEV' in method:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                      # Autolevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.get_VSA_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level

    def set_freq(self, freq):
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq

    def set_VSA_init(self):
        self.VSA.write('INIT:CONT OFF')                                 # Single Sweep
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                            # Trigger External
        self.VSA.write(':SENS:NR5G:FRAM:COUN:AUTO OFF')                 # Frame count off
        self.VSA.write(':SENS:NR5G:FRAM:COUN 1')                        # Single frame
        self.VSA.write(':SENS:NR5G:FRAM:SLOT 1')                        # Single Slot
        self.VSA.write(':SENS:SWE:TIME 0.0005')                         # Capture Time
        self.VSA.write(':CONF:NR5G:DL:CC1:RFUC:STAT OFF')               # Phase compensation
        # VSA.write(':SENS:NR5G:RSUM:CCR ALL')                          # CA View all CC results

    def set_VSG_init(self):
        self.VSG.write(':SOUR1:CORR:OPT:EVM 1')                         # Optimize EVM
        self.VSG.write(':SOUR1:BB:NR5G:TRIG:OUTP1:MODE REST')           # Maker Mode Arb Restart
        self.VSG.write(':SOUR1:BB:NR5G:NODE:RFPH:MODE 0')               # Phase Compensation Off


if __name__ == '__main__':
    林 = option_functions()
    林.get_info()
