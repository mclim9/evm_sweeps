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
        self.VSA.write(":CONF:STAN 12")                     # bn:12 be:11 ax:10
        self.VSA.write(":SENS:SWE:TIME 0.001")
        self.VSA.write(":SENS:DEM:TXAR OFF")
        self.VSA.write(":SENS:DEM:CEST 0")
        self.VSA.write(":SENS:DEM:INT:WIEN:DSPR:STAT MANUAL")
        self.VSA.write(":CALC1:MARK1:X 0")
        self.VSA.write(":SENS:DEM:INT:WIEN:DSPR 3.00")

    def vsa_get_attn_ref(self) -> Tuple[str, float, str]:
        attn = self.VSA.query("INP:ATT?")
        refl = self.VSA.queryFloat("DISP:TRAC:Y:SCAL:RLEV?")
        prea = self.VSA.query('INP:GAIN:STAT?')                         # Preamp State
        return attn, refl, prea

    @method_timer
    def vsa_get_ACLR(self):
        self.VSA.write(':CONF:BURS:SPEC:ACLR:IMM')
        self.vsa_sweep()
        ACLRV = self.VSA.query(':CALC:MARK:FUNC:POW:RES? ACP')          # ACLR Relative
        print(f'{ACLRV}')
        return ACLRV

        pass

    def vsa_get_ch_power(self) -> float:
        # chPw = self.VSA.queryFloat('FETC:BURS:PAYL?')
        self.vsa_sweep()
        self.vsa_sweep()
        chPw = self.VSA.queryFloat(':CALC1:MARK:Y?')
        return chPw

    @method_timer
    def vsa_get_evm(self):
        self.vsa_sweep()
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
        # freq = int(self.VSA.query(":SENS1:FREQ:CENT?")) / 1e9
        std = self.VSA.query(":CONF:STAN?")
        bw = self.VSA.query(":SENS:POW:ACH:CBW?")
        mcs = self.VSA.query("CONF:WLAN:RUC:SEGM1:CHAN1:RUL1:USER1:MCS?")
        rtnStr = f"WiFi_{std}_{bw}_MCS{mcs}"
        # rtnStr = "6.0GHz_11AC_160_MCS0_1234A-MPDU"
        self.Wavename = rtnStr
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
            self.VSA.write(f'DISP:TRAC:Y:SCAL:RLEV {pwr + 4}')          # FSW
            # self.VSA.write(f':INP1:RLEV {pwr + 4}')                     # FSWX
        return 0.0

    @method_timer
    def vsa_sweep(self):
        """VSA take a single sweep"""
        self.VSA.write('INIT:CONT OFF')
        self.VSA.query('INIT:IMM;*OPC?')
