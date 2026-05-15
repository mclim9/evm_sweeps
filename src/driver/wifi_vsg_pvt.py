from helper.utils import method_timer
from helper.bench_config import BenchConfig
from driver.base_vsg import VSGDriver


class WiFi_VSG(VSGDriver):
    def __init__(self, VSG=None):
        self.VSG = VSG or BenchConfig().VSG_start()

    @method_timer
    def vsg_configure(self) -> None:
        self.VSG.write("SOUR:GPRF:GEN1:STAT ON")
        # self.VSG.write("SOUR:GPRF:GEN1:ARB:FILE <ARBFile>")

    def vsg_get_extra(self) -> str:
        return "none"

    def vsg_save_state(self):
        pass

    def vsg_set_frequency(self, freq: float) -> None:
        self.VSG.write(f":SOUR:GPRF:GEN1:RFS:FREQ {freq}")

    def vsg_set_power(self, pwr: float) -> None:
        self.VSG.write(f"SOUR:GPRF:GEN1:RFS:LEV {pwr}")
