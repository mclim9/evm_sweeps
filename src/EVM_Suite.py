from EVM_Sweep_Simple import EVM_Sweep

def main():
    from driver.NR5G_FR1_meas import std_insr_driver            # standard to use
    sweep = EVM_Sweep()
    sweep.meas = std_insr_driver()
    sweep.freq_arry = [int(1.00e9), int(2.00e9), int(3.00e9), int(4.00e9), int(5.00e9), int(6.00e9), int(7.00e9)]    # FR1 Freqs
    sweep.pwr_arry = range(-45, 15, 1)
    sweep.lvl_arry = ['LEV']                                    # LEV:autolevel EVM:autoEVM
    sweep.main()

    from driver.WiFi_meas import std_insr_driver                # standard to use
    sweep.meas = std_insr_driver()
    sweep.freq_arry = [int(2.4e9), int(5.000e9), int(6.00e9)]   # 802.11 Freqs
    sweep.pwr_arry = range(-45, 15, 1)
    sweep.lvl_arry = ['LEV']                                    # LEV:autolevel EVM:autoEVM
    sweep.main()


if __name__ == '__main__':
    main()
