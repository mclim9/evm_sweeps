from typing import Tuple
from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsa import VSADriver
import os

class VSA_driver(VSADriver):
    def __init__(self, VSA=None):
        self.VSA = VSA or BenchConfig().VSA_start()
        self.VSA.s.settimeout(30)   # For AutoEVM

    def vsa_configure(self) -> None:
        self.VSA.query("*RST;*OPC?")
        self.VSA.query(":SYST:DISP:UPD ON; *OPC?")
        self.VSA.query(':INST:CRE:NEW WLAN, "WLAN"; *OPC?')
        self.VSA.write(":INIT:CONT ON")
        self.VSA.write(":CONF:STAN 10")                     # be:11 ax:10
        self.VSA.write(":SENS:SWE:TIME 0.002")
        self.VSA.write(":SENS:DEM:TXAR OFF")
        self.VSA.write(":SENS:DEM:CEST 0")
        self.VSA.write(":SENS:DEM:INT:WIEN:DSPR:STAT MANUAL")
        self.VSA.write(":SENS:DEM:INT:WIEN:DSPR 3.00")

    def vsa_get_attn_ref(self) -> Tuple[str, float]:
        attn = self.VSA.query("INP:ATT?")
        ref_lvl = self.VSA.queryFloat("DISP:TRAC:Y:SCAL:RLEV?")
        return attn, ref_lvl

    @method_timer
    def vsa_get_ACLR(self):
        pass

    def vsa_get_ch_power(self) -> float:
        return 999.0

    @method_timer
    def vsa_get_evm(self):
        self.VSA.write("INIT:CONT OFF")
        self.VSA.query("INIT:IMM;*OPC?")
        raw = self.VSA.query(":FETC:BURS:EVM:DATA:AVER?").split(",")
        try:
            evm = float(raw[0])
        except Exception:
            evm = 999.0
        return evm

    def vsa_get_extra(self, extra=None) -> str:
        extra = extra.upper() if extra else ''
        if extra == 'IQNC':
            self.VSA.query(':SENS:ADJ:NCAN:AVER:STAT ON; *OPC?')        # IQNC On
            self.VSA.write(':SENS:ADJ:NCAN:AVER:COUN 10')               # IQNC Averaging
        elif extra == 'XCORR':
            self.VSA.query(':SENS:IQ:XCOR:STAT ON; *OPC?')              # XCorr On
        extra = f'WiFi EVM {extra if extra else ""}'.strip()
        return extra

    def vsa_get_waveform_info(self) -> str:
        # freq = int(self.VSG.query(":SOUR1:FREQ:CW?")) / 1e9
        # std = self.VSG.query(":SOUR1:BB:WLNN:FBL1:TMOD?")
        # bw = self.VSG.query(":SOUR1:BB:WLNN:BW?")
        # mcs = self.VSG.query(":SOUR1:BB:WLNN:FBL1:USER1:MCS?")
        # data = self.VSG.query(":SOUR1:BB:WLNN:FBL1:USER1:DATA:LENG?")
        # rtnStr = f"{freq}GHz_{std}_{bw}_{mcs}_{data}A-MPDU"
        rtnStr = "6.0GHz_11AC_160_MCS0_1234A-MPDU"
        return rtnStr

    def vsa_save_state(self):
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

    def vsa_set_frequency(self, freq: float) -> None:
        self.VSA.write(f":SENSE:FREQ:CENT {freq}")

    @method_timer
    def vsa_set_level(self, mode: str) -> float:
        if mode == "LEV" or mode == "EVM":
            self.VSA.query(":CONF:POW:AUTO ONCE;*OPC?")
        else:
            self.VSA.write(f':INP:ATT:AUTO ON')                         # AutoAttenuation
            pwr = self.vsa_get_ch_power()
            self.VSA.write(f':FETC:POW:OUTP:CURR:RES {pwr + 2}')        # Manually set ref level
        return 0.0
