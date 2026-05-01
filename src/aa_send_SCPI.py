from helper.bench_config import bench

if __name__ == '__main__':
    sweep = bench()
    sweep.VSA = bench().VSA_start('10.102.72.32')
    print(sweep.VSA.query('*IDN?'))
    asdf = sweep.VSA.query(':FETC:CC1:ISRC:FRAM:SUMM:ALL?')
    sweep.VSA.write(':SENS:ADJ:LEV;*WAI')
    pass
