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
        '''VSA FR2 Config'''
        self.VSA.query('*RST;*OPC?')                            # Reset
        self.VSA.query(':SYST:DISP:UPD ON; *OPC?')              # Display on
        self.VSA.query(':INST:CRE:NEW NR5G, "5G NR"; *OPC?')    # Start 5GNR
        self.VSA.write(':CONF:NR5G:LDIR UL')                    # Link Direction
        self.VSA.write(':CONF:NR5G:UL:CC1:TPR OFF')             # TPrecode
        self.VSA.write(':CONF:NR5G:UL:CC1:DFR HIGH')            # Band
        self.VSA.write(f':CONF:NR5G:UL:CC1:BW BW{self.bw}')     # BW
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:SSP SS{self.scs}') # SCS
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:CSL 1')    # User Config Slot
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBC {self.rb}')   # BWP RB
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBOF {self.rbo}') # BWP RB Offset
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBC {self.rb}')
        self.VSA.write(f':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBOF {self.rbo}')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:MOD Q1K')

        # Additional Settings
        self.VSA.query(':LAY:ADD:WIND? "2",ABOV,EVSC')          # EVM vs Sym vs Carr
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                    # Trigger External
        self.VSA.write(':SENS:NR5G:FRAM:COUN:AUTO OFF')         # Frame count off
        self.VSA.write(':SENS:NR5G:FRAM:COUN 1')                # Single frame
        self.VSA.write(':SENS:NR5G:FRAM:SLOT 1')                # Single Slot
        self.VSA.write(':UNIT:EVM DB')                          # EVM Units: DB PCT
        self.VSA.write(':SENS:SWE:TIME 0.0005')                 # Capture Time
        self.VSA.write(':CONF:NR5G:UL:CC1:RFUC:STAT OFF')       # Phase compensation

    def VSA_Load(self, file):
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save 5G State"""
        self.VSA.query(f'*IDN?')
        self.VSA.query(f'MMEM:STOR:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        # HST_IP = self.VSA.s.getsockname()[0]                  # Host PC
        FSW_IP = self.VSA.s.getpeername()[0]                    # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    @method_timer
    def VSG_Config(self):
        '''Config w/ SMW 5G Quick Settings'''
        self.VSG.write(f':SOUR1:BB:NR5G:LINK UP')               # Link Direction
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:DUPL FDD')     # FDD TDD
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CARD FR2_1')   # FR2
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CBW BW{self.bw}')      # BW50 BW100
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:SCSP SCS{self.scs}')   # Sub Carrier Spacing
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:MOD QAM1024')# Modulation
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:RBN {self.rb}')     # num RB
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:RBOF {self.rbo}')   # RB Offset
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:APPL')             # QS Apply
        self.VSG.write(f':SOUR1:BB:NR5G:STAT 1')                # BB On

        # Additional Settings
        self.VSG.write(f':OUTP1:STAT 1')                        # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')           # Optimize EVM
        self.VSG.write(':SOUR1:BB:NR5G:TRIG:OUTP1:MODE REST')   # Maker Mode Arb Restart
        self.VSG.write(':SOUR1:BB:NR5G:NODE:RFPH:MODE 0')       # Phase Compensation Off

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

    @method_timer
    def get_VSA_sweep(self):
        self.VSA.write('INIT:CONT OFF')                                 # Cont Sweep off
        self.VSA.query('INIT:IMM;*OPC?')                                # Single Sweep

    def set_VSx_freq(self, freq):
        self.VSA.write(f':SENS:FREQ:CENT {freq}')
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')


if __name__ == '__main__':
    林 = config()
    林.freq = 18e9          # Center Frequency, Hz: 24e9; 28e9; 39e9; 43e9
    林.scs  = 120           # Sub Carr Spacing: 60; 120;
    林.rb   = 66            # number RB
    林.rbo  = 0             # RB Offset
    林.bw   = 100           # 50; 100; 200; 400
    std_config(林)
