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
        self.VSA.query(':INST:CRE:NEW WLAN, "WLAN"; *OPC?')     # Start 5GNR6
        self.VSA.write(':INIT:CONT OFF')                        # Single Sweep
        self.VSA.write(':CONF:STAN 11')                         # 11:be
        self.VSA.write(':SENS:SWE:TIME 0.002')                  # Sweep Time
        self.VSA.write(':SENS:DEM:TXAR OFF')                    # Burst Search
        self.VSA.write(':SENS:DEM:CEST 0')                      # ChEst 1:Payload 0:Pre Only
        # self.VSA.write(':SENS:DEM:CEST:PAYL 0')               # ChEst Payload
        # self.VSA.write(':SENS:DEM:CEST:RANG PRE2T')           # ChEst PRE1T(Preamble) PRE1T(Data)
        self.VSA.write(':SENS:DEM:INT:WIEN:DSPR:STAT MANUAL')   # Wiener Filter
        self.VSA.write(':SENS:DEM:INT:WIEN:DSPR 0.03')          # Wiener Filter
        # self.VSA.write(':SENS:BAND:CHAN:AUTO:TYPE MB320')     # Meas 320MHz
        # self.VSA.write('CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:USER1:MCS 13')

        self.VSA.write(':LAY:REPL:WIND "3",RSDetailed')         # Detailed Result Summary

    def VSA_Load(self, file):
        self.VSA.write(f':MMEM:LOAD:DEM:C1 "{file}"')

    def VSA_save_state(self):
        """VSA Save State"""
        self.VSA.query(f'*IDN?')
        # BW   = self.VSA.query(':SENS:BAND:CHAN:AUTO:TYPE?')
        BW   = self.VSA.queryInt(':TRAC:IQ:SRAT?') / 1e6
        PCKT = self.VSA.query(':FETC:BURS:PPDU:TYPE?')
        Dir  = self.VSA.query(':CONF:WLAN:RUC:EHTP?')
        Mod  = self.VSA.query(':CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:USER1:MCS?')
        RUS  = self.VSA.query(':CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:RUS?')
        # Pwr  = self.VSA.query(':FETC:BURS:PAYL?')
        # EVM  = self.VSA.query(':FETC:BURS:EVM:ALL:AVER?')
        if Dir == 'MU':
            Dir = 'Down'
        else:
            Dir = 'Up'
        self.Wavename = f'WiFi{BW}_{PCKT}_{Dir}_{RUS}_MCS{Mod}'
        self.VSA.query(f':MMEM:STOR:STAT 1,"C:\\R_S\\instr\\{self.Wavename}.dfl";*OPC?')
        FSW_IP = self.VSA.s.getpeername()[0]                    # Instr
        os.system(f'start \\\\{FSW_IP}')

    def VSG_Config(self):
        '''Settings'''
        self.VSG.write(f':SOUR1:BB:WLNN:BW BW320')                  # 320MHz BW
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:TMOD EHT320')          # Tx Mode
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:USER1:MCS MCS13')      # MCS
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:USER1:RUTY RU4996')    # RU Config
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:USER1:MPDU1:COUN 10')  # Num MPDU
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:GUAR GD08')            # Guard Duration
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:SYMD SD64')            # Symbol Duration
        self.VSG.write(f':SOUR1:BB:WLNN:FBL1:ITIM 0')               # Idle Time
        self.VSG.write(f':SOUR1:BB:WLNN:CLIP:SPPS 1')               # Signal Field Clipping
        self.VSG.write(f':SOUR1:BB:WLNN:STAT 1')                    # BB On

        # Additional Settings
        self.VSG.write(f':OUTP1:STAT 1')                        # RF On
        self.VSG.query(':SOUR1:CORR:OPT:EVM 1;*OPC?')           # Optimize EVM
        self.VSG.write(':SOUR1:BB:WLNN:TRIG:OUTP1:MODE REST')   # Maker Mode Arb Restart

    def VSG_save_state(self):
        """VSG Save 5G State"""
        self.VSG.query(f'*IDN?')
        BW   = self.VSG.query(':SOUR1:BB:WLNN:BW?')
        PCKT = self.VSG.query(':SOUR1:BB:WLNN:FBL1:TMOD?')
        Dir  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:LINK?')
        Mod  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:MCS?')
        RUS  = self.VSG.query(':SOUR1:BB:WLNN:FBL1:USER1:RUTY?')

        self.Wavename = f'WiFi{BW}_{PCKT}_{Dir}_{RUS}_{Mod}'
        self.VSG.query(f':SOUR1:BB:WLNN:SETT:STOR "/var/user/{self.Wavename}";*OPC?')
        SMW_IP = self.VSG.s.getpeername()[0]        # Instr
        os.system(f'start \\\\{SMW_IP}\\user')


if __name__ == '__main__':
    林 = config()
    # 林.VSG_Config()
    # 林.VSA_Config()
    # 林.VSG_save_state()
    林.VSA_save_state()
