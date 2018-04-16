'''
Read in flow-through data.
'''

import pandas as pd


def read_file(fileloc):
    '''Read in SCS file given by fileloc. Return df with lon/lat included.

    Example:
    import read
    loc = '/Users/kthyng/Documents/data/HRRO1 (HRR_Leg2) September 27-29 2017/SCS_ Point Sur/PS18_09_Leg2_Whilden_SCS/Sea-Bird-Thermosalinograph-(converted-ASCII-data)_20170927-162751.Raw'
    df = scs.read_file(loc)
    '''

    if 'Thermosalinograph' in fileloc:
        df = pd.read_table(fileloc, parse_dates=[[0,1]], index_col=0, sep=',|\s+',
                           header=0, usecols=[0,1,3,4,5], engine='python',
                           names=['Dates [UTC?]', '', 'Conductivity', 'Practical salinity', 'Temperature'])
    else:
        print('not ready to read in that file yet.')

    # read in gps data
    gpsfile = '/'.join(fileloc.split('/')[:-1]) + '/ASHTECH-$GPGGA-RAW_' + fileloc.split('/')[-1].split('_')[-1]
    gps = pd.read_csv(gpsfile, parse_dates=[[0,1]], index_col=0, header=0,
                      usecols=[0,1,4,6], names=['Dates [UTC?]', '', 'lat', 'lon'])

    # convert from shoved-together numbers to decimal degrees by pulling apart
    # number as a string
    gps.loc[:,'lat'] = [int(str(la)[:2]) + float(str(la)[2:])/60 for la in gps['lat']]
    # same for longitude
    gps.loc[:,'lon'] = [-(int(str(lo)[:2]) + float(str(lo)[2:])/60) for lo in gps['lon']]


    # combine together
    # accounting for known issue for interpolation after sampling if indices changes
    # https://github.com/pandas-dev/pandas/issues/14297
    # interpolate on union of old and new index
    gps_union = gps.reindex(gps.index.union(df.index)).interpolate(method='time')
    # reindex to the new index
    gps = gps_union.reindex(df.index)

    df['lat'] = gps['lat']
    df['lon'] = gps['lon']

    return df
