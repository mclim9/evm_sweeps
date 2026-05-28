from helper.bench_config import bench

if __name__ == '__main__':
    林 = bench()
    林.VSA = bench().VSA_start('192.168.58.102')
    print(林.VSA.query('*IDN?'))
    # 林.VSA.write("CONF:REFS:CWF:FPAT '/home/instrument/test.wv'")
    txty = 林.VSA.query('FETC:BURS:PEAK?')
    print(txty)
    # 林.VSA.clear_error()
    # asdf = sweep.VSA.query(':FETC:CC1:ISRC:FRAM:SUMM:ALL?')
    # sweep.VSA.write(':SENS:ADJ:LEV;*WAI')
