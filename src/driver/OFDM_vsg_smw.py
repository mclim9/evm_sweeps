from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsg import VSGDriver


class VSG_driver(VSGDriver):
    def __init__(self, VSG=None):
        self.VSG = VSG or BenchConfig().VSG_start()
        self.xml = '/var/user/Leo/LEO_WV_example'

    @method_timer
    def vsg_configure(self) -> None:
        self.VSG.write(":SOUR1:BB:OFDM:STAT 1")
        self.VSG.write(":OUTP1:STAT 1")
        self.VSG.write(f":SOUR1:BB:OFDM:SETT:LOAD '{self.xml}'")
        self.VSG.query(":SOUR1:CORR:OPT:EVM 1;*OPC?")
        self.sampling = self.VSG.query(":SOUR1:BB:OFDM:SAMP?")
        # self.VSG.write(":SOUR1:BB:WLNN:TRIG:OUTP1:MODE REST")

    def vsg_get_extra(self, extra=None) -> str:
        return "SMW-OFDM"

    def vsg_save_state(self):
        pass

    def vsg_set_frequency(self, freq: float) -> None:
        self.VSG.query(f":SOUR1:FREQ:CW {freq};*OPC?")          # SMW

    def vsg_set_power(self, pwr: float) -> None:
        self.VSG.query(f":SOUR1:POW:POW {pwr};*OPC?")           # SMW
