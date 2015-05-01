import os
from jellyrisk_forecaster.utils import download_myocean_data, exists, create_if_not_exists
from jellyrisk_forecaster.config import settings


LAT_MIN = '35.8'
LAT_MAX = '36.1'
LONG_MIN = '14.1'
LONG_MAX = '14.6'

TIMES_START_MEDSEA_REAN_006_004 = ['2011-01-01']
TIMES_END_MEDSEA_REAN_006_004 = ['2012-12-26']

TIME_START_PHYS_006_001 = ['2013-01-01']
TIME_END_PHYS_006_001 = ['2014-09-17']

DATASETS = [
    # PHYSICAL VARIABLES
    # 2007-2012
    {
        # salinity
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS',
        'product': 'myov05-med-ingv-sal-rean-dm',
        'times_start': TIMES_START_MEDSEA_REAN_006_004,
        'times_end': TIMES_END_MEDSEA_REAN_006_004,
        'vars': ['vosaline']
    },
    {   # temperature
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS',
        'product': 'myov05-med-ingv-tem-rean-dm',
        'times_start': TIMES_START_MEDSEA_REAN_006_004,
        'times_end': TIMES_END_MEDSEA_REAN_006_004,
        'vars': ['votemper']
    },
    {   # ocean currents
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS',
        'product': 'myov05-med-ingv-cur-rean-dm',
        'times_start': TIMES_START_MEDSEA_REAN_006_004,
        'times_end': TIMES_END_MEDSEA_REAN_006_004,
        'vars': ['vozocrtx', 'vomecrty']
    },
    # > 2013
    {   # salinity
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov05-med-ingv-sal-an-fc-dm',
        'times_start': TIME_START_PHYS_006_001,
        'times_end': TIME_END_PHYS_006_001,
        'vars': ['vosaline']
    },
    {   # temperature
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov05-med-ingv-tem-an-fc-dm',
        'times_start': TIME_START_PHYS_006_001,
        'times_end': TIME_END_PHYS_006_001,
        'vars': ['votemper']
    },
    {   # ocean currents
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov05-med-ingv-cur-an-fc-dm',
        'times_start': TIME_START_PHYS_006_001,
        'times_end': TIME_END_PHYS_006_001,
        'vars': ['vozocrtx', 'vomecrty']
    },
    # BIOLOGICAL
    {   # MEDSEA_REANALYSIS_BIO_006_008
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_BIO_006_008-TDS',
        'product': 'myov04-med-ogs-bio-rean',
        'module': 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
        'times_start': TIMES_START_MEDSEA_REAN_006_004,
        'times_end': TIMES_END_MEDSEA_REAN_006_004,
        'vars': ['chl', 'nit', 'pcb', 'pho', 'dox', 'npp']
    },
    {   # MEDSEA_ANALYSIS_FORECAST_BIO_006_006
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS',
        'product': 'myov04-med-ogs-bio-an-fc',
        'module': 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
        'times_start': TIME_START_PHYS_006_001,
        'times_end': TIME_END_PHYS_006_001,
        'vars': ['chl', 'nit', 'pcb', 'pho', 'dox', 'npp']
    },
]


folder = os.path.join(settings.DATA_FOLDER, 'Malta', 'Historical')
create_if_not_exists(folder)

for dataset in DATASETS:
    for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
        filename = 'malta-%(product)s_%(time_start)s_%(time_end)s.nc' % \
            {'product': dataset['product'],
             'time_start': time_start,
             'time_end': time_end}
        if not exists(filename, folder):
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
