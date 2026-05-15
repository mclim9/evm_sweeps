from typing import Tuple
from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsa import VSADriver


class WiFi_VSA(VSADriver):
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

    def vsa_get_extra(self) -> str:
        return "none"

    def vsa_get_waveform_info(self) -> str:
        # freq = int(self.VSG.query(":SOUR1:FREQ:CW?")) / 1e9
        # std = self.VSG.query(":SOUR1:BB:WLNN:FBL1:TMOD?")
        # bw = self.VSG.query(":SOUR1:BB:WLNN:BW?")
        # mcs = self.VSG.query(":SOUR1:BB:WLNN:FBL1:USER1:MCS?")
        # data = self.VSG.query(":SOUR1:BB:WLNN:FBL1:USER1:DATA:LENG?")
        # rtnStr = f"{freq}GHz_{std}_{bw}_{mcs}_{data}A-MPDU"
        rtnStr = "6.0GHz_11AC_160_MCS0_1234A-MPDU"
        return rtnStr

    def vsa_set_frequency(self, freq: float) -> None:
        self.VSA.write(f":SENSE:FREQ:CENT {freq}")

    def vsa_set_level(self, mode: str) -> float:
        if mode == "LEV" or mode == "EVM":
            self.VSA.query(":CONF:POW:AUTO ONCE;*OPC?")
            return 0.0

        self.VSA.write(":INP:ATT:AUTO ON")
        pwr = self.vsa_get_ch_power()
        self.VSA.write(f":DISP:WIND:TRAC:Y:SCAL:RLEV {pwr - 2}")
        return 0.0
