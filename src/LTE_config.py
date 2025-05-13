""" Rohde & Schwarz Automation for demonstration use."""
import os
from bench_config import bench
from utils import method_timer, std_config

class config():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSG = bench().VSG_start()

    @method_timer
    def VSA_Config(self):
        '''VSA WLAN Config'''
        self.VSA.query('*RST;*OPC?')                                    # Reset
        self.VSA.query(f':INST:CRE:NEW LTE, "LTE";*OPC?')               # Opens LTE Mode
        self.VSA.write(f':TRIG:SEQ:SOUR EXT;*WAI')                      # Trigger: IMM|EXT|EXT2|RFP|IFP|TIME|VID|BBP|PSEN
        self.VSA.write(f':INIT:CONT ON;*WAI')                           # Continuous sweep: ON|OFF
        self.VSA.write(f':CONF:LTE:DUPL FDD;*WAI')                      # Duplexing:  FDD|TDD
        self.VSA.write(f':CONF:LTE:LDIR UL;*WAI')                       # Link direction: UL|DL
        self.VSA.write(f':CONF:LTE:UL:CC:BW BW{self.bw}_00;*WAI')       # Channel BW: BW1_40|BW3_00|BW5_00|BW10_00|BW15_00|BW20_00
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:RBC {self.rbc}')    # Num RB: 0 to 100
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:rboF {self.rbo}')   # RB Offset: 0 to 99
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:MOD QAM256')         # Modulation
        self.VSA.write(f':SENS:SWE:TIME 0.00201;*WAI')                  # Sweep Time: Range: 0.00201s to 0.0501
        self.VSA.write(f':SENS:LTE:FRAM:SSUB ON;*WAI')                  # Single SUbframe Mode: ON|OFF
        # self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                        # Auto Level

        # Other Settings
        self.VSA.write(f':SYST:DISP:UPD ON')                            # Turns on VSA display: ON|OFF
        self.VSA.query(f':INIT:IMM;*OPC?')                              # Run Single

    def VSA_Load(self, file):
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save LTE State"""
        self.VSA.query(f'*IDN?')

        ldir = self.VSA.query(':CONF:LTE:LDIR?')                        # link direction
        dupl = self.VSA.query(':CONF:LTE:DUPL?')                        # duplex mode
        ldir = "UL" if ldir == "UL" else "DL"
        chbw = self.VSA.query(f':CONF:LTE:{ldir}:CC:BW?')
        rbn  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:RBC?')
        rbo  = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:CLUS1:rboF?')
        cmod = self.VSA.query(f':CONF:LTE:{ldir}:CC:SUBF0:ALL:MOD?')

        self.Wavename = f'LTE_{ldir}_{dupl}_{chbw}_{rbn}RB_{rbo}rbo_{cmod}'
        self.VSA.query(f'MMEM:STOR:CC:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        FSW_IP = self.VSA.s.getpeername()[0]            # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def VSG_Config(self):
        '''Settings'''
        self.VSG.write(f':SOUR1:BB:EUTR:STDM LTE')                              # 4G Std: LTE|EUTRA|IOT
        self.VSG.write(f':SOUR1:BB:EUTR:DUPL FDD')                              # Duplexing: FDD|TDD
        self.VSG.write(f':SOUR1:BB:EUTR:LINK UP')                               # Link direction: UP|DOWN
        self.VSG.write(f':SOUR1:BB:EUTR:UL:BW BW{self.bw}_00')                  # Ch BW: BW1_40|BW3_00|BW5_00|BW10_00|BW15_00|BW20_00|BW0_20|USER
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:RBC {self.rbc}')   # Num of RBs: Range: 0 to 110
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:VRB {self.rbo}')   # RB Offset: Range 0 to 49
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:MOD QAM256')   # RB Offset: Range 0 to 49
        self.VSG.write(f':SOUR1:BB:EUTR:STAT 1')                                # BB State: 0|1
        self.VSG.query(f':SOUR1:POW:LEV:IMM:AMPL -10;*OPC?')                    # CW power: Range:-130 - +30dBm

        # Additional Settings
        self.VSG.write(f':OUTP1:STAT 1')                                        # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')                           # Optimize EVM
        self.VSG.write(':SOUR1:BB:EUTR:TRIG:OUTP1:MODE REST')                   # Maker Mode Arb Restart

    def VSG_save_state(self):
        """VSG Save WLAN State"""
        self.VSG.query(f'*IDN?')
        ldir = self.VSG.query(':SOUR1:BB:EUTR:LINK?')
        dupl = self.VSG.query(':SOUR1:BB:EUTR:DUPL?')
        if ldir == 'UP':
            ldir  = 'UL'
            Mod  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:MOD?')
            rbn  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:RBC?')
            rbo  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:VRB?')
            chbw = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:BW?')
        elif ldir == 'DOWN':
            ldir  = 'DL'
            Mod  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:MOD?')
            rbn  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:RBC?')
            rbo  = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:CELL0:SUBF0:ALL0:PUSC:SET1:VRB?')
            chbw = self.VSG.query(f':SOUR1:BB:EUTR:{ldir}:BW?')
        self.Wavename = f'LTE_{ldir}_{dupl}_{chbw}_{rbn}RB_{rbo}rbo_{Mod}'
        self.VSG.query(f':SOUR1:BB:EUTR:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        SMW_IP = self.VSG.s.getpeername()[0]        # Instr
        os.system(f'start \\\\{SMW_IP}\\user')

    @method_timer
    def get_VSA_sweep(self):
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    def set_VSx_freq(self, freq):
        self.VSA.write(f':SENS:FREQ:CENT {freq}')
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')
        self.VSA.query(f':INIT:IMM;*OPC?')                              # Run Single


if __name__ == '__main__':
    林 = config()
    林.rbc = 24             # Num RB
    林.rbo = 0              # RB Offset
    林.bw  = 5              # Ch BW, MHz 3; 5; 10; 15; 20
    林.freq = 6e9           # Center Frequency, Hz
    std_config(林)
