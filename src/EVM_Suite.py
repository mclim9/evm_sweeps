from pathlib import Path
import logging

from helper.bench_config import BenchConfig
from EVM_Sweep import SweepConfig, SweepRunner
from driver.wifi_vsa_fsw import WiFi_VSA
from driver.wifi_vsg_pvt import WiFi_VSG


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    bench = BenchConfig()
    vsa = WiFi_VSA(bench.VSA_start())
    vsg = WiFi_VSG(bench.VSG_start())

    config = SweepConfig(
        freq_arry=[int(2.4e9), int(5.0e9), int(6.0e9)],
        pwr_arry=range(-45, 15, 1),
        lvl_arry=['LEV'],
        output_dir=Path('results'),
        file_prefix='wifi_evm_sweep'
    )

    runner = SweepRunner(vsa, vsg, config)
    runner.run()


if __name__ == '__main__':
    main()
