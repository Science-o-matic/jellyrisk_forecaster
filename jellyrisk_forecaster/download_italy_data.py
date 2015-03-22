# 2009-02-15 a 2009-12-06
# 2010-01-24 a 2010-12-19
# 2011-01-01 a 2011-12-29
# 2012-01-02 a 2012-12-30

from multiprocessing import Pool
from multiprocessing.pool import IMapIterator
import time


# To stop using ^C
# https://gist.github.com/aljungberg/626518
def wrapper(func):
    def wrap(self, timeout=None):
        return func(self, timeout=timeout if timeout is not None else 1e100)
    return wrap
IMapIterator.next = wrapper(IMapIterator.next)


import os
from datetime import datetime, timedelta

from jellyrisk_forecaster.config import settings
from jellyrisk_forecaster.utils import download_myocean_data, exists

start = datetime(2009, 1, 1)
end = datetime(2014, 12, 31)
#times_start = ['2009-01-01']
#times_end = ['2012-12-31']

dt_format = '%Y-%m-%d'
# descargamos del 2009 al final de 2013
# lat: [35.498497219999997, 45.802202780000002]
# lon: [0.13078611100000001, 21.06455278]

med_times_start = []
med_times_end = []
cur_start = start
while cur_start <= end:
    cur_end = cur_start + timedelta(days=30)
    time_start = cur_start.strftime(dt_format)
    time_end = cur_end.strftime(dt_format)

    med_times_start.append(time_start)
    med_times_end.append(time_end)

    cur_start = cur_end + timedelta(days=1)


chlostart = [datetime(2013, 1, 1) + timedelta(31) * i for i in range(0, 11)]
chloend = [dt + timedelta(30) for dt in chlostart]

datasets = [
    {   # salinity
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-sal-an-fc',
        'variables': ['vosaline'],
        'times_start': med_times_start,
        'times_end': med_times_end
    },
    {   # temperature
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-tem-an-fc',
        'variables': ['votemper'],
        'times_start': med_times_start,
        'times_end': med_times_end
    },
    {   # ocean currents
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-cur-an-fc',
        'variables': ['vozocrtx', 'vomecrty'],
        'times_start': med_times_start,
        'times_end': med_times_end
    },
    {   # chlorophile >= 2013
        'service': 'http://purl.org/myocean/ontology/service/database#OCEANCOLOUR_MED_CHL_L3_NRT_OBSERVATIONS_009_040-TDS',
        'product': 'dataset-oc-med-chl-modis_a-l3-chl_1km_daily-rt-v02',
        'variables': ['CHL'],
        'module': 'http://myocean.artov.isac.cnr.it/mis-gateway-servlet/Motu',
        'times_start': [dt.strftime(dt_format) for dt in chlostart],
        'times_end': [dt.strftime(dt_format) for dt in chloend],

    }
]
folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Italy')
long_min = '0'
long_max = '22'
lat_min = '35'
lat_max = '46'

# print(times_start)
# print(times_end)


def download_dataset(dataset):
    for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
        filename = 'italy-{start}-{end}-{product}.nc'.format(
            start=time_start, end=time_end, product=dataset['product'])
        if not exists(filename, folder):
            download_myocean_data(
                service=dataset['service'],
                product=dataset['product'],
                variables=dataset['variables'],
                module=dataset.get('module', None),
                time_start=time_start, time_end=time_end,
                long_min=long_min, long_max=long_max,
                lat_min=lat_min, lat_max=lat_max,
                filename='italy-{start}-{end}-{product}.nc'.format(
                    start=time_start, end=time_end, product=dataset['product']),
                folder=folder)
            time.sleep(30)
        else:
            print('File {} found, skipping...'.format(filename))


pool = Pool(1)
results = pool.imap(download_dataset, datasets)
for i, _ in enumerate(results, 1):
    print(i)
pool.close()
pool.join()
