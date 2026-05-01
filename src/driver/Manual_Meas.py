from utils import method_timer, std_meas, std_config
from bench_config import bench
import os

class std_insr_driver():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSA.s.settimeout(30)   # For AutoEVM
        self.VSG = bench().VSG_start()
        self.freq = 18e9            # Center Frequency, Hz: 24e9; 28e9; 39e9; 43e9
        self.scs  = 120             # Sub Carr Spacing: 60; 120;
        self.rb   = 66              # number RB
        self.rbo  = 0               # RB Offset
        self.bw   = 100             # 50; 100; 200; 400

    @method_timer
    def VSA_Config(self):
        '''VSA FR1 Config'''
        self.VSA.query(':SYST:DISP:UPD ON; *OPC?')              # Display on

    @method_timer
    def VSA_get_ACLR(self):
        pass

    def VSA_get_attn_reflvl(self):
        attn = self.VSA.query('INP:ATT?')                               # Input Attn
        refl = self.VSA.queryFloat('DISP:TRAC:Y:SCAL:RLEV?')            # Ref Level
        return attn, refl

    def VSA_get_chPwr(self):
        chPw = self.VSA.queryFloat(':FETC:CC1:ISRC:FRAM:SUMM:POW?')     # VSA CW Ch Pwr
        return chPw

    @method_timer
    def VSA_get_EVM(self):
        try:
            self.VSA.query('INIT:IMM;*OPC?')                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        except:                                                         # noqa
            print('EVM 2nd Try')
            self.VSA.query('INIT:IMM;*OPC?')                            # Take a sweep
            EVM = self.VSA.queryFloat(':FETC:CC1:SUMM:EVM:ALL:AVER?')   # VSA CW
        return EVM

    def VSA_get_info(self):
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

    @method_timer
    def VSA_level(self, method='LEV'):
        '''# LEV:autolevel EVM:autoEVM'''
        if 'EVM' in method:
            self.VSA.query(f':SENS:ADJ:EVM;*OPC?')                      # AutoEVM
        elif 'LEV' in method:
            self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                      # Autolevel
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.get_VSA_chPwr()
            self.VSA.write(f':DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}')    # Manually set ref level

    def VSA_Load(self, file):
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save 5G State"""
        self.VSA.query(f'*IDN?')
        self.VSA.query(f'MMEM:STOR:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        # HST_IP = self.VSA.s.getsockname()[0]                          # Host PC
        FSW_IP = self.VSA.s.getpeername()[0]                            # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def VSA_sweep(self):
        self.VSA.write('INIT:CONT OFF')
        self.VSA.query('INIT:IMM;*OPC?')

    @method_timer
    def VSG_Config(self):
        '''Config w/ SMW 5G Quick Settings'''
        self.VSG.query(f'*IDN?')                                        # Link Direction

    def VSG_pwr(self, pwr):
        self.VSG.write(f':SOUR1:POW:POW {pwr}')                         # VSG Power

    def VSG_save_state(self):
        """VSG Save 5G State"""
        self.VSG.query(f'*IDN?')
        Band = self.VSG.query(':SOUR1:BB:NR5G:NODE:CELL0:CARD?')
        Dir  = self.VSG.query(':SOUR1:BB:NR5G:LINK?')
        BW   = self.VSG.query(':SOUR1:BB:NR5G:NODE:CELL0:CBW?')
        if Dir == 'UP':
            SCS  = self.VSG.query(':SOUR1:BB:NR5G:UBWP:USER0:CELL0:UL:BWP0:SCSP?')
            Mod  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL0:MOD?')
            RBN  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL0:RBN?')
            Dir  = 'UL'
        elif Dir == 'DOWN':
            SCS  = self.VSG.query(':SOUR1:BB:NR5G:UBWP:USER0:CELL0:DL:BWP0:SCSP?')
            Mod  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL1:MOD?')
            RBN  = self.VSG.query(':SOUR1:BB:NR5G:SCH:CELL0:SUBF0:USER0:BWP0:ALL1:RBN?')
            Dir  = 'DL'

        self.Wavename = f'{Band}_{Dir}_{SCS}SCS_{BW}_{RBN}RB_{Mod}'
        self.VSG.query(f':SOUR1:BB:NR5G:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        # HST_IP = self.VSG.s.getsockname()[0]                          # Host PC
        SMW_IP = self.VSG.s.getpeername()[0]                            # Instr
        os.system(f'start \\\\{SMW_IP}\\user')

    def VSx_freq(self, freq):
        # self.VSA.write(f':CONF:NR5G:GMCF {freq}')                     # Ana CA Center Freq
        self.VSA.write(f':SENSE:FREQ:CENT {freq}')                      # Ana CC Center Freq
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')                        # Generator center freq


if __name__ == '__main__':
    std_config(std_insr_driver())
    std_meas(std_insr_driver())
