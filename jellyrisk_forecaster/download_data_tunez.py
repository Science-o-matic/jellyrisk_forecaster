import os
from jellyrisk_forecaster import utils
from jellyrisk_forecaster.config import settings

TIME_START = ['2013-01-01']
TIME_END = ['2015-01-07']

DATASETS = [
    {   # salinity
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov05-med-ingv-sal-an-fc-dm',
        'times_start': TIME_START,
        'times_end': TIME_END,
        'vars': ['vosaline']
    },
    {   # temperature
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov05-med-ingv-tem-an-fc-dm',
        'times_start': TIME_START,
        'times_end': TIME_END,
        'vars': ['votemper']
    },
    {   # ocean currents
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov05-med-ingv-cur-an-fc-dm',
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
    {   # MEDSEA_ANALYSIS_FORECAST_BIO_006_006
        'service': 'http://purl.org/myocean/ontology/service/database#WIND_GLO_WIND_L4_NRT_OBSERVATIONS_012_004',
        'product': 'CERSAT-GLO-BLENDED_WIND_L4-V3-OBS_FULL_TIME_SERIE',
        'module': 'http://www.ifremer.fr/mis-gateway-servlet/Motu',
        'times_start': TIME_START,
        'times_end': TIME_END,
        'vars': ['eastward_wind', 'wind_speed', 'northward_wind'],
        'depth_min': '10',
        'depth_max': '10.0001'
    },
]


def download_historical_data(datasets, force=False):
    """
    Download historical data from MyOcean using motu-client.
    """
    folder = os.path.join(settings.DATA_FOLDER, 'Tunez', 'Historical')
    utils.create_if_not_exists(folder)

    for dataset in DATASETS:
        for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
            filename = 'tunez-%(product)s_%(time_start)s_%(time_end)s.nc' % \
                {'product': dataset['product'],
                 'time_start': time_start,
                 'time_end': time_end}
            if not utils.exists(filename, folder) or force:
                print('Downloading %s...' % filename)
                utils.download_myocean_data(
                    service=dataset['service'],
                    product=dataset['product'],
                    variables=dataset['vars'],
                    module=dataset.get('module', None),
                    time_start=time_start,
                    time_end=time_end,
                    long_min='9.8', long_max='10.9',
                    lat_min='35.7', lat_max='37.4',
                    depth_min=dataset.get('depth_min', settings.DEPTH_MIN),
                    depth_max=dataset.get('depth_max', settings.DEPTH_MAX),
                    folder=folder,
                    filename=filename)
            else:
                print('File %s already exists, skipping download... (use force=True to override).' % filename)


download_historical_data(DATASETS)

beaches_path = os.path.join(settings.DATA_FOLDER, 'Tunez', 'Tunez_beaches.csv')
in_folder = os.path.join(settings.DATA_FOLDER, 'Tunez', 'Historical')
out_folder = os.path.join(settings.DATA_FOLDER, 'Tunez', 'Historical', 'Preprocessed')
utils.extract_historical_data(DATASETS, beaches_path, in_folder, out_folder, prefix='tunez-')
