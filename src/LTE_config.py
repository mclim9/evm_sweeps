""" Rohde & Schwarz Automation for demonstration use."""
import os
from bench_config import bench

class config():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSG = bench().VSG_start()

    def VSA_Config(self):
        self.VSA.query('*RST;*OPC?')                                    # Reset
        self.VSA.tick()
        self.VSA.query(f':INST:CRE:NEW LTE, "LTE";*OPC?')               # Opens LTE Mode
        self.VSA.write(f':TRIG:SEQ:SOUR EXT;*WAI')                      # Trigger: IMM|EXT|EXT2|RFP|IFP|TIME|VID|BBP|PSEN
        self.VSA.write(f':INIT:CONT OFF;*WAI')                          # Continuous sweep: ON|OFF
        self.VSA.write(f':CONF:LTE:DUPL FDD;*WAI')                      # Duplexing:  FDD|TDD
        self.VSA.write(f':CONF:LTE:LDIR UL;*WAI')                       # Link direction: UL|DL
        self.VSA.write(f':CONF:LTE:UL:CC:BW BW5_00;*WAI')               # Channel BW: BW1_40|BW3_00|BW5_00|BW10_00|BW15_00|BW20_00
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:RBC {rbc}')    # Num RB: 0 to 100
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:CLUS1:RBOF {rbo}')   # RB Offset: 0 to 99
        self.VSA.write(f':CONF:LTE:UL:CC:SUBF0:ALL:MOD QAM256')         # Modulation
        self.VSA.write(f':SENS:SWE:TIME 0.00201;*WAI')                  # Sweep Time: Range: 0.00201s to 0.0501
        self.VSA.write(f':SENS:LTE:FRAM:SSUB ON;*WAI')                  # Single SUbframe Mode: ON|OFF
        # self.VSA.query(f':SENS:ADJ:LEV;*OPC?')                        # Auto Level

        # Other Settings
        self.VSA.write(f':SYST:DISP:UPD ON')                            # Turns on VSA display: ON|OFF
        self.VSA.query(f':INIT:IMM;*OPC?')                              # Run Single
        self.VSA.tock('LTE VSA Config')
        self.VSA.clear_error()

    def VSA_Load(self, file):
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save State"""
        self.VSA.query(f'*IDN?')
        Dir  = self.VSA.query(':CONF:LTE:LDIR?')
        Dupl = self.VSA.query(':CONF:LTE:DUPL?')
        if Dir == 'UP':
            Dir  = 'UL'
        elif Dir == 'DOWN':
            Dir  = 'DL'
        Mod  = self.VSA.query(f':CONF:LTE:{Dir}:CC:SUBF0:ALL:MOD?')
        RBN  = self.VSA.query(f':CONF:LTE:{Dir}:CC:SUBF0:ALL:CLUS1:RBC?')
        RBO  = self.VSA.query(f':CONF:LTE:{Dir}:CC:SUBF0:ALL:CLUS1:RBOF?')
        BW   = self.VSA.query(f':CONF:LTE:{Dir}:CC:BW?')
        self.Wavename = f'LTE_{Dir}_{Dupl}_{BW}_{RBN}RB_{RBO}RBO_{Mod}'
        self.VSA.query(f'MMEM:STOR:CC:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        FSW_IP = self.VSA.s.getpeername()[0]            # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    def VSG_Config(self):
        '''Settings'''
        self.VSG.tick()
        self.VSG.write(f':SOUR1:BB:EUTR:STDM LTE')                              # 4G Std: LTE|EUTRA|IOT
        self.VSG.write(f':SOUR1:BB:EUTR:DUPL FDD')                              # Duplexing: FDD|TDD
        self.VSG.write(f':SOUR1:BB:EUTR:LINK UP')                               # Link direction: UP|DOWN
        self.VSG.write(f':SOUR1:BB:EUTR:UL:BW BW5_00')                          # Ch BW: BW1_40|BW3_00|BW5_00|BW10_00|BW15_00|BW20_00|BW0_20|USER
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:RBC {rbc}')   # Num of RBs: Range: 0 to 110
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:SET1:VRB {rbo}')   # RB Offset: Range 0 to 49
        self.VSG.write(f':SOUR1:BB:EUTR:UL:CELL0:SUBF0:ALL0:PUSC:MOD QAM256')   # RB Offset: Range 0 to 49
        self.VSG.write(f':SOUR1:BB:EUTR:STAT 1')                                # BB State: 0|1
        self.VSG.query(f':SOUR1:POW:LEV:IMM:AMPL -10;*OPC?')                    # CW power: Range:-130 - +30dBm
        self.VSG.tock('LTE VSG Config')

        # Additional Settings
        self.VSG.write(f':OUTP1:STAT 1')                                        # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')                           # Optimize EVM
        self.VSG.write(':SOUR1:BB:EUTR:TRIG:OUTP1:MODE REST')                   # Maker Mode Arb Restart
        self.VSG.clear_error()

    def VSG_save_state(self):
        """VSG Save State"""
        self.VSG.query(f'*IDN?')
        Dir  = self.VSG.query(':SOUR1:BB:EUTR:LINK?')
        Dupl = self.VSG.query(':SOUR1:BB:EUTR:DUPL?')
        if Dir == 'UP':
            Dir  = 'UL'
            Mod  = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:CELL0:SUBF0:ALL0:PUSC:MOD?')
            RBN  = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:CELL0:SUBF0:ALL0:PUSC:SET1:RBC?')
            RBO  = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:CELL0:SUBF0:ALL0:PUSC:SET1:VRB?')
            BW   = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:BW?')
        elif Dir == 'DOWN':
            Dir  = 'DL'
            Mod  = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:CELL0:SUBF0:ALL0:PUSC:MOD?')
            RBN  = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:CELL0:SUBF0:ALL0:PUSC:SET1:RBC?')
            RBO  = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:CELL0:SUBF0:ALL0:PUSC:SET1:VRB?')
            BW   = self.VSG.query(f':SOUR1:BB:EUTR:{Dir}:BW?')
        self.Wavename = f'LTE_{Dir}_{Dupl}_{BW}_{RBN}RB_{RBO}RBO_{Mod}'
        self.VSG.query(f':SOUR1:BB:EUTR:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        SMW_IP = self.VSG.s.getpeername()[0]        # Instr
        os.system(f'start \\\\{SMW_IP}\\user')

    def set_freq(self, freq):
        self.VSA.write(f':SENS:FREQ:CENT {freq}')
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')
        self.VSA.query(f':INIT:IMM;*OPC?')                                                        # Run Single


if __name__ == '__main__':
    rbc = 24
    rbo = 0
    林 = config()
    林.VSG_Config()
    林.VSA_Config()
    林.set_freq(7e9)
    # 林.VSG_save_state()
    # 林.VSA_save_state()
