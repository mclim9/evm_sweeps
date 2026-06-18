from helper.bench_config import bench

if __name__ == '__main__':
    林 = bench()
    # 林.VSA = bench().VSA_start('fswx3-42-101442')
    林.VSA = bench().VSA_start('172.24.225.101')
    林.VSA.query('*IDN?', 1)
    林.VSA.query(':INP:GAIN:STAT?', 1)
    林.VSA.clear_error()
    # 林.VSA.query("BB:ARB:WAV:TAG? 'TYPE'")
    # 林.VSA.query("BB:ARB:WAV:TAG? 'DATE'")
    # 林.VSA.query("BB:ARB:WAV:TAG? 'SAMPLES'")
    # 林.VSA.query("BB:ARB:WAV:TAG? 'CLOCK'")
    # 林.VSA.query("BB:ARB:WAV:TAG? 'LEVEL OFFS'")
    # 林.VSA.query("BB:ARB:WAV:TAG? 'MARKER LIST 1'")
    # 林.VSA.clear_error()
    # asdf = sweep.VSA.query(':FETC:CC1:ISRC:FRAM:SUMM:ALL?')
    # sweep.VSA.write(':SENS:ADJ:LEV;*WAI')
