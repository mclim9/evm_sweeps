import os
from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsg import VSGDriver


class WiFi_VSG(VSGDriver):
    def __init__(self, VSG=None):
        self.VSG = VSG or BenchConfig().VSG_start()

    @method_timer
    def vsg_configure(self) -> None:
        self.VSG.write(":SOUR1:BB:WLNN:BW BW320")
        self.VSG.write(":SOUR1:BB:WLNN:FBL1:TMOD EHT320")
        self.VSG.write(":SOUR1:BB:WLNN:FBL1:USER1:MCS MCS13")
        self.VSG.write(":SOUR1:BB:WLNN:FBL1:USER1:RUTY RU4996")
        self.VSG.write(":SOUR1:BB:WLNN:FBL1:USER1:MPDU1:COUN 50")
        self.VSG.write(":SOUR1:BB:WLNN:FBL1:GUAR GD08")
        self.VSG.write(":SOUR1:BB:WLNN:FBL1:SYMD SD64")
        self.VSG.write(":SOUR1:BB:WLNN:FBL1:ITIM 0")
        self.VSG.write(":SOUR1:BB:WLNN:CLIP:SPPS 1")
        self.VSG.write(":SOUR1:BB:WLNN:STAT 1")
        self.VSG.write(":OUTP1:STAT 1")
        self.VSG.query(":SOUR1:CORR:OPT:EVM 1;*OPC?")
        self.VSG.write(":SOUR1:BB:WLNN:TRIG:OUTP1:MODE REST")
        self.VSG.write("SOUR:GPRF:GEN1:ARB:FILE ''")

    def vsg_get_extra(self) -> str:
        return "none"

    def vsg_save_state(self):
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

    def vsg_set_frequency(self, freq: float) -> None:
        self.VSG.write(f":SOUR1:FREQ:CW {freq}")              # SMW

    def vsg_set_power(self, pwr: float) -> None:
        self.VSG.write(f":SOUR1:POW:POW {pwr}")             # SMW
