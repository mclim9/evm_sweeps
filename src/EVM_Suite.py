from pathlib import Path
import logging

from helper.bench_config import BenchConfig
from EVM_Sweep import SweepConfig, SweepRunner
# from driver.wifi_vsa_fsw import VSA_driver
from driver.K18_vsa_fsw import VSA_driver
# from driver.wifi_vsa_fsw import VSA_driver as VSA_K91_driver
# from driver.wifi_vsg_pvt import VSG_driver
from driver.NR5G_FR1_vsa_fsw import VSA_driver as VSA_K144_driver
from driver.NR5G_FR1_vsg_pvt import VSG_driver


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    bench = BenchConfig()
    vsa = VSA_driver(bench.VSA_start())
    vsg = VSG_driver(bench.VSG_start())

    config = SweepConfig(
        # freq_arry=[int(2.4e9), int(5.0e9), int(6.0e9)],         # WiFi
        freq_arry=[int(1.00e9), int(2.00e9), int(3.00e9), int(4.00e9), int(5.00e9)],         # FR1
        pwr_arry=list(range(-45, 15, 1)),
        lvl_arry=['MAN'],
        output_dir=Path('results'),
        file_prefix='5GNR_FR1_evm_sweep'
    )

    # runner = SweepRunner(vsa, vsg, config)
    # runner.run()

    # Run w/ native VSA driver
    vsa = VSA_K144_driver(bench.VSA_start())
    runner = SweepRunner(vsa, vsg, config)
    runner.run()


if __name__ == '__main__':
    main()
