""" Rohde & Schwarz Automation for demonstration use."""
import os
from bench_config import bench

class config():
    def __init__(self):
        self.VSA = bench().VSA_start()
        self.VSG = bench().VSG_start()

    def VSA_Config(self):
        '''Read Frame config from VSG'''
        self.VSA.query('*RST;*OPC?')                            # Reset
        self.VSA.query(':SYST:DISP:UPD ON; *OPC?')              # Display on
        self.VSA.query(':INST:CRE:NEW NR5G, "5G NR"; *OPC?')    # Start 5GNR6
        self.VSA.write(':CONF:NR5G:LDIR UL')                    # Link Direction
        self.VSA.write(':CONF:NR5G:UL:CC1:TPR ON')              # TPrecode
        self.VSA_Config_FR1()

        # Additional Settings
        self.VSA.write(':LAY:ADD:WIND? "2",ABOV,EVSC')          # EVM vs Sym vs Carr
        self.VSA.write(':TRIG:SEQ:SOUR EXT')                    # Trigger External
        self.VSA.write(':SENS:NR5G:FRAM:COUN:AUTO OFF')         # Frame count off
        self.VSA.write(':SENS:NR5G:FRAM:COUN 1')                # Single frame
        self.VSA.write(':SENS:NR5G:FRAM:SLOT 1')                # Single Slot
        self.VSA.write(':UNIT:EVM DB')                          # EVM Units: DB PCT
        self.VSA.write(':CONF:NR5G:UL:CC1:RFUC:STAT OFF')       # Phase compensation

    def VSA_Config_FR1(self):
        self.VSA.write(':CONF:NR5G:UL:CC1:DFR MIDD')            # Band
        self.VSA.write(':CONF:NR5G:UL:CC1:BW BW100')            # BW
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SSP SS30') # SCS
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:CSL 1')    # User Config Slot
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBC 270')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBOF 0')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBOF 0')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBC 270')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:MOD QAM256')
        self.VSA.write(':SENS:SWE:TIME 0.0005')                 # Capture Time


    def VSA_Config_FR2(self):
        self.VSA.write(':CONF:NR5G:UL:CC1:DFR HIGH')            # Band
        self.VSA.write(':CONF:NR5G:UL:CC1:BW BW100')            # BW
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SSP SS120')# SCS
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:CSL 1')    # User Config Slot
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBC 66')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:RBOF 0')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBOF 0')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:RBC 66')
        self.VSA.write(':CONF:NR5G:UL:CC1:FRAM1:BWP0:SLOT0:ALL0:MOD Q1K')
        self.VSA.write(':SENS:SWE:TIME 0.0002')                 # Capture Time

    def VSA_Load(self, file):
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save 5G State"""
        self.VSA.query(f'*IDN?')
        self.VSA.query(f'MMEM:STOR:DEM "C:\\R_S\\instr\\{self.Wavename}.allocation";*OPC?')
        # HST_IP = self.VSA.s.getsockname()[0]        # Host PC
        FSW_IP = self.VSA.s.getpeername()[0]        # Instr
        os.system(f'start \\\\{FSW_IP}\\instr')

    def VSG_Config(self):
        '''Config w/ SMW 5G Quick Settings'''
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:APPL')             # QS Apply
        self.VSG.write(f':SOUR1:BB:NR5G:STAT 1')                # BB On
        self.VSG_Config_FR1()

        # Additional Settings
        self.VSG.write(f':OUTP1:STAT 1')                        # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')           # Optimize EVM
        self.VSG.write(':SOUR1:BB:NR5G:TRIG:OUTP1:MODE REST')   # Maker Mode Arb Restart
        self.VSG.write(':SOUR1:BB:NR5G:NODE:RFPH:MODE 0')       # Phase Compensation Off
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:TP:STAT 1') # TPre

    def VSG_Config_FR1(self):
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:DUPL FDD')     # FDD TDD
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CARD FR1GT3')  # FR1GT3
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CBW BW100')    # BW50 BW100
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:SCSP SCS30')   # Sub Carrier Spacing
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:MOD QAM256')# Modulation
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:RBN 273')   # RB

    def VSG_Config_FR2(self):
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:DUPL FDD')     # FDD TDD
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CARD FR2_1')   # FR1GT3
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:CBW BW100')    # BW50 BW100
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:SCSP SCS120')  # Sub Carrier Spacing
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:MOD QAM1024')# Modulation
        self.VSG.write(f':SOUR1:BB:NR5G:QCKS:GEN:ES:RBN 66')    # RB

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
        # HST_IP = self.VSG.s.getsockname()[0]        # Host PC
        SMW_IP = self.VSG.s.getpeername()[0]        # Instr
        os.system(f'start \\\\{SMW_IP}\\user')

    def set_freq(self, freq):
        self.VSA.write(f':SENS:FREQ:CENT {freq}')
        self.VSG.write(f':SOUR1:FREQ:CW {freq}')


if __name__ == '__main__':
    林 = config()
    林.VSG_Config()
    林.VSA_Config()
    林.set_freq(2e9)
    # 林.VSG_save_state()
    # 林.VSA_save_state()
