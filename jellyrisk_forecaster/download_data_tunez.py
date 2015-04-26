import os
from jellyrisk_forecaster.utils import download_myocean_data, exists, create_if_not_exists
from jellyrisk_forecaster.config import settings

TIME_START = ['2013-01-01']
TIME_END = ['2015-01-07']

DATASETS = [
    {   # salinity
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-sal-an-fc',
        'times_start': TIME_START,
        'times_end': TIME_END,
        'vars': ['vosaline']
    },
    {   # temperature
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-tem-an-fc',
        'times_start': TIME_START,
        'times_end': TIME_END,
        'vars': ['votemper']
    },
    {   # ocean currents
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-cur-an-fc',
        'times_start': TIME_START,
        'times_end': TIME_END,
        'vars': ['vozocrtx', 'vomecrty']
    },
    {   # MEDSEA_ANALYSIS_FORECAST_BIO_006_006
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS',
        'product': 'myov04-med-ogs-bio-an-fc',
        'module': 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
        'times_start': TIME_START,
        'times_end': TIME_END,
        'vars': ['chl', 'nit', 'pcb', 'pho', 'dox', 'npp']
    },
]


def download_historical_data(datasets, force=False):
    """
    Download historical data from MyOcean using motu-client.
    """
    folder = os.path.join(settings.DATA_FOLDER, 'Tunez', 'Historical')
    create_if_not_exists(folder)

    for dataset in DATASETS:
        for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
            filename = 'tunez-%(product)s_%(time_start)s_%(time_end)s.nc' % \
                {'product': dataset['product'],
                 'time_start': time_start,
                 'time_end': time_end}
            if not exists(filename, folder) or force:
                print('Downloading %s...' % filename)
                download_myocean_data(
                    service=dataset['service'],
                    product=dataset['product'],
                    variables=dataset['vars'],
                    module=dataset.get('module', None),
                    time_start=time_start,
                    time_end=time_end,
                    long_min='9.8', long_max='10.9',
                    lat_min='35.7', lat_max='37.4',
                    folder=folder,
                    filename=filename)
            else:
                print('File %s already exists, skipping download... (use force=True to override).' % filename)


download_historical_data(DATASETS)
