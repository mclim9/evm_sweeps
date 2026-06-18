from pathlib import Path
import logging

from helper.bench_config import BenchConfig
from EVM_Sweep import SweepConfig, SweepRunner
# from Sweep_ACLR import SweepConfig, SweepRunner
# from driver.wifi_vsa_fsw import VSA_driver
# from driver.K18_vsa_fsw import VSA_driver
from driver.NR5G_FR1_vsa_fsw import VSA_driver
# from driver.wifi_vsa_fsw import VSA_driver as VSA_K91_driver
# from driver.wifi_vsg_pvt import VSG_driver
from driver.NR5G_FR1_vsg_smw import VSG_driver


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    bench = BenchConfig()
    vsa = VSA_driver(bench.VSA_start())
    vsg = VSG_driver(bench.VSG_start())
    vsa.rb   = 1092                # number RB
    vsa.rbo  = 114                 # RB Offset
    vsa.bw   = 500                 # 10; 50; 100
    vsg.rb   = 1092                # number RB
    vsg.rbo  = 114                 # RB Offset
    vsg.bw   = 500                 # 10; 50; 100

    config = SweepConfig(
        # freq_arry=[int(2.4e9), int(5.0e9), int(6.0e9)],                                   # WiFi
        freq_arry=[int(1.00e9), int(2.00e9), int(3.00e9), int(4.00e9), int(5.00e9), int(6.00e9), int(7.00e9), int(8.00e9)],        # FR1
        pwr_arry=list(range(-45, 15, 1)),
        lvl_arry=['MAN'],
        output_dir=Path('test_results'),
        file_prefix='5GNR_FR1_ACLR',
        vsa_extra=None,
        vsg_extra=None
    )

    runner = SweepRunner(vsa, vsg, config)
    config.vsa_extra = "XCorr_RMS"
    runner.run()
    config.vsa_extra = "ACLR_RMS"
    runner.run()

    # Run w/ native VSA driver
    # vsa = VSA_driver(bench.VSA_start())
    # runner = SweepRunner(vsa, vsg, config)
    # runner.run()


if __name__ == '__main__':
    main()
