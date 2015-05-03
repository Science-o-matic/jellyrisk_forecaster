import os
from subprocess import call
import pandas as pd

from jellyrisk_forecaster import utils
from jellyrisk_forecaster.config import settings, BASE_DIR


TIMES_START_MEDSEA_REAN_006_004 = ['2007-05-23', '2008-05-28', '2009-05-16',
                                   '2010-05-15', '2011-06-01', '2012-06-05']
TIMES_END_MEDSEA_REAN_006_004 = ['2007-09-18', '2008-09-23', '2009-09-22',
                                 '2010-09-23', '2011-10-01', '2012-09-23']
TIMES_START_MEDSEA_FOR_006_001 = ['2013-06-03']
TIMES_END_MEDSEA_FOR_006_001 = ['2013-10-23']

TIMES_OCEANCOLOUR_MED_CHL_073 = [
    ('2007-05-23', '2007-09-18'),
    ('2008-05-28', '2008-09-23'),
    ('2009-05-16', '2009-09-22'),
    ('2010-05-15', '2010-09-23'),
    ('2011-06-01', '2011-10-01'),
    ('2012-06-05', '2012-07-31'),
]

TIMES_OCEANCOLOUR_MED_CHL_040 = [
    # ('2012-08-01', '2012-09-23'),
    ('2013-06-03', '2013-10-23')
]

DATASETS = [
    # PHYSICAL VARIABLES
    # 2007-2012
    {
        # salinity
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS',
        'product': 'myov04-med-ingv-sal-rean-dm',
        'times_start': TIMES_START_MEDSEA_REAN_006_004,
        'times_end': TIMES_END_MEDSEA_REAN_006_004,
        'vars': ['vosaline']
    },
    {   # temperature
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS',
        'product': 'myov04-med-ingv-tem-rean-dm',
        'times_start': TIMES_START_MEDSEA_REAN_006_004,
        'times_end': TIMES_END_MEDSEA_REAN_006_004,
        'vars': ['votemper']
    },
    {   # ocean currents
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS',
        'product': 'myov04-med-ingv-cur-rean-dm',
        'times_start': TIMES_START_MEDSEA_REAN_006_004,
        'times_end': TIMES_END_MEDSEA_REAN_006_004,
        'vars': ['vozocrtx', 'vomecrty']
    },
    # 2013
    {   # salinity
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-sal-an-fc',
        'times_start': TIMES_START_MEDSEA_FOR_006_001,
        'times_end': TIMES_END_MEDSEA_FOR_006_001,
        'vars': ['vosaline']
    },
    {   # temperature
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-tem-an-fc',
        'times_start': TIMES_START_MEDSEA_FOR_006_001,
        'times_end': TIMES_END_MEDSEA_FOR_006_001,
        'vars': ['votemper']
    },
    {   # ocean currents
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        'product': 'myov04-med-ingv-cur-an-fc',
        'times_start': TIMES_START_MEDSEA_FOR_006_001,
        'times_end': TIMES_END_MEDSEA_FOR_006_001,
        'vars': ['vozocrtx', 'vomecrty']
    },

    # BIOLOGICAL
    {   # chlorophile 1
        'service': 'http://purl.org/myocean/ontology/service/database#OCEANCOLOUR_MED_CHL_L3_REP_OBSERVATIONS_009_073-TDS',
        'product': 'dataset-oc-med-chl-multi_cci-l3-chl_4km_daily-rep-v02',
        'module': 'http://myocean.artov.isac.cnr.it/mis-gateway-servlet/Motu',
        'times_start': [start for start, end in TIMES_OCEANCOLOUR_MED_CHL_073],
        'times_end': [end for start, end in TIMES_OCEANCOLOUR_MED_CHL_073],
        'vars': ['CHL']
    },
    {   # chlorophile 2
        'service': 'http://purl.org/myocean/ontology/service/database#OCEANCOLOUR_MED_CHL_L3_NRT_OBSERVATIONS_009_040-TDS',
        'product': 'dataset-oc-med-chl-modis_a-l3-chl12_1km_daily-rt-v02',
        'module': 'http://myocean.artov.isac.cnr.it/mis-gateway-servlet/Motu',
        'times_start': [start for start, end in TIMES_OCEANCOLOUR_MED_CHL_040],
        'times_end': [end for start, end in TIMES_OCEANCOLOUR_MED_CHL_040],
        'vars': ['CHL']
    },
    {   # MEDSEA_ANALYSIS_FORECAST_BIO_006_006
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS',
        'product': 'myov04-med-ogs-bio-an-fc',
        'module': 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
        'times_start': ['2013-06-03'],
        'times_end': ['2013-10-23'],
        'vars': ['chl', 'nit', 'pcb', 'pho', 'dox', 'npp']
    },
    {   # MEDSEA_REANALYSIS_BIO_006_007
        'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_BIO_006_007-TDS',
        'product': 'myov04-med-ogs-bio-rean',
        'module': 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
        'times_start': ['2007-05-01', '2008-05-01', '2009-05-01', '2010-05-01'],
        'times_end': ['2007-10-01', '2008-10-01', '2009-10-01', '2010-10-01'],
        'vars': ['chl', 'nit', 'pcb', 'pho', 'dox', 'npp']
    },

]


def download_historical_data(datasets, force=False):
    """
    Download historical data from MyOcean using motu-client.
    """
    folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical')
    utils.create_if_not_exists(folder)

    for dataset in DATASETS:
        for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
            filename = '%(product)s_%(time_start)s_%(time_end)s.nc' % \
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
                    folder=folder,
                    filename=filename)
            else:
                print('File %s already exists, skipping download... (use force=True to override).' % filename)


def preprocess_historical_data(datasets, force=False):
    """Preprocess environmental historical data from MyOcean and merge it with
    inspection vars.

    If the output file is already present and force is False, skip preprocessing.
    """
    # concatenate temporarily and merge all environmental data
    vosaline, votemper, vozocrtx, vomecrty = concatenate_historical_data(datasets)
    all_vars = votemper.merge(vosaline.merge(vozocrtx.merge(vomecrty)))

    # concatenate temporarily all inspection data
    fnames = ['SSS_2007-2010.csv', 'SSS_2011.csv', 'SSS_2012.csv', 'SSS_2013.csv']
    paths = [os.path.join(settings.DATA_FOLDER, 'DailyInspections', fname) for fname in fnames]
    observations = [pd.read_csv(path, sep='\t') for path in paths]
    obs_concated = pd.concat(observations)

    # merge environmental and inspection data
    everything = all_vars.merge(obs_concated)
    filename = 'Environmental_and_Inspections_2010-2013.csv'
    out_path = os.path.join(settings.DATA_FOLDER, filename)

    if not os.path.exists(out_path) or force:
        print('Creating %s...' % filename)
        with open(out_path, 'w') as out_file:
            everything.to_csv(out_file, sep='\t', na_rep='NA', index=False)
    else:
        print('\nFile %s already exists, skipping preprocessing... (use force=True to override).' % out_path)


def concatenate_historical_data(datasets):
    """
    Concatenate temporarily all environmental data.
    """
    def get_path(dataset, var, time_start, time_end):
        folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical', 'Preprocessed')
        filename = '%(product)s_%(time_start)s_%(time_end)s-%(var)s.csv' % \
            {'product': dataset['product'],
             'time_start': time_start,
             'time_end': time_end,
             'var': var}
        return os.path.join(folder, filename)

    def concat(datasets, var):
        paths = []
        for dataset in datasets:
            for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
                paths.append(get_path(dataset, var, time_start, time_end))
        dfs = [pd.read_csv(path, sep='\t') for path in paths]
        return pd.concat(dfs)

    vosaline = concat((datasets[0], datasets[3]), 'vosaline')
    votemper = concat((datasets[1], datasets[4]), 'votemper')
    vozocrtx = concat((datasets[2], datasets[5]), 'vozocrtx')
    vomecrty = concat((datasets[2], datasets[5]), 'vomecrty')

    return (vosaline, votemper, vozocrtx, vomecrty)


def calibrate_model(force=False):
    """Calibrate model using historical data.

    If a file with the model is already present and force=False, skip."""
    folder = settings.DATA_FOLDER
    filename = 'Pnoctiluca_model.R'

    if not utils.exists(filename, folder) or force:
        os.chdir(settings.DATA_FOLDER)
        with open(os.path.join(BASE_DIR, 'R', 'Pnoctiluca_calibrate.R'), 'r') as inputfile:
            call(["R", "--no-save"], stdin=inputfile)
    else:
        print('\nFile %s already exists, skipping modelling... (use force=True to override).' % filename)


def calibrate(force=False):
    print("\n=== Calibrating model from historical data... ===")
    download_historical_data(DATASETS, force)

    beaches_path = os.path.join(settings.DATA_FOLDER, 'Geo', 'beaches.txt')
    in_folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical')
    out_folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical', 'Preprocessed')
    utils.extract_historical_data(DATASETS, beaches_path, in_folder, out_folder, force)
    preprocess_historical_data(DATASETS, force)
    calibrate_model(force)

if __name__ == "__main__":
    calibrate()
