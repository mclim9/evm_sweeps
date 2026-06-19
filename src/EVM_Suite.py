from helper.bench_config import BenchConfig
from pathlib import Path
import logging

# Sweeper
from EVM_Sweep import SweepConfig, SweepRunner
# from Sweep_ACLR import SweepConfig, SweepRunner

# VSA Driver
# from driver.wifi_vsa_fsw import VSA_driver
# from driver.K18_vsa_fsw import VSA_driver
from driver.NR5G_FR1_vsa_fsw import VSA_driver
# from driver.wifi_vsa_fsw import VSA_driver as VSA_K91_driver

# VSG Driver
# from driver.wifi_vsg_pvt import VSG_driver
from driver.NR5G_FR1_vsg_smw import VSG_driver


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    bench = BenchConfig()
    vsa = VSA_driver(bench.VSA_start())
    vsg = VSG_driver(bench.VSG_start())

    config = SweepConfig(
        # freq_arry=[int(2.4e9), int(5.0e9), int(6.0e9)],                                   # WiFi
        freq_arry=[int(1.00e9), int(2.00e9), int(3.00e9), int(4.00e9), int(5.00e9), int(6.00e9), int(7.00e9), int(8.00e9)],        # FR1
        pwr_arry=list(range(-45, 15, 1)),
        lvl_arry=['LEV', 'MAN'],                    # MAN; LEV;
        output_dir=Path('test_results'),
        file_prefix='5GNR_FR1_EVM_400MHz',
        vsa_extra=None,
        vsg_extra=None
    )

    vsa.rb   = 1092                   # number RB
    vsa.rbo  = 114                    # RB Offset
    vsa.bw   = 500                    # 10; 50; 100
    vsg.rb   = vsa.rb                 # number RB
    vsg.rbo  = vsa.rbo                # RB Offset
    vsg.bw   = vsa.bw                 # 10; 50; 100

    runner = SweepRunner(vsa, vsg, config)
    # config.vsa_extra = "ACLR_RMS"     # IQNC; XCORR; ACLR_RMS; XCORR_RMS
    runner.run()

    # Run w/ native VSA driver
    # vsa = VSA_driver(bench.VSA_start())
    # runner = SweepRunner(vsa, vsg, config)
    # runner.run()


if __name__ == '__main__':
    main()
