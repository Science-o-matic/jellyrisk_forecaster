import os
from subprocess import call
import pandas as pd

from jellyrisk_forecaster.utils import exists
from jellyrisk_forecaster.utils import download_myocean_data, create_if_not_exists
from jellyrisk_forecaster.config import settings, BASE_DIR


TIMES_START_MEDSEA_REAN_006_004 = ['2007-05-23', '2008-05-28', '2009-05-16',
                                   '2010-05-15', '2011-06-01', '2012-06-05']
TIMES_END_MEDSEA_REAN_006_004 = ['2007-09-18', '2008-09-23', '2009-09-22',
                                 '2010-09-23', '2011-10-01', '2012-09-23']
TIMES_START_MEDSEA_FOR_006_001 = ['2013-06-03']
TIMES_END_MEDSEA_FOR_006_001 = ['2013-10-23']

DATASETS = [
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
]


def download_historical_data(datasets, force=False):
    """
    Download historical data from MyOcean using motu-client.
    """
    folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical')
    create_if_not_exists(folder)

    for dataset in DATASETS:
        for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
            filename = '%(product)s_%(time_start)s_%(time_end)s.nc' % \
                {'product': dataset['product'],
                 'time_start': time_start,
                 'time_end': time_end}
            if not exists(filename, folder) or force:
                print('Downloading %s...' % filename)
                download_myocean_data(
                    service=dataset['service'],
                    product=dataset['product'],
                    time_start=time_start,
                    time_end=time_end,
                    folder=folder,
                    filename=filename)
            else:
                print('File %s already exists, skipping download... (use force=True to override).' % filename)


def extract_historical_data(datasets, force=False):
    """
    Extract variables values for all dates and beaches.

    If the output file is already present and force is False, skip preprocessing.
    """
    nc_folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical')

    out_folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical', 'Preprocessed')
    create_if_not_exists(out_folder)

    for dataset in DATASETS:
        for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
            nc_filename = '%(product)s_%(time_start)s_%(time_end)s.nc' % \
                {'product': dataset['product'],
                 'time_start': time_start,
                 'time_end': time_end}
            nc_filepath = os.path.join(nc_folder, nc_filename)

            for var in dataset['vars']:
                out_filename = '%(product)s_%(time_start)s_%(time_end)s-%(var)s.csv' % \
                    {'product': dataset['product'],
                     'time_start': time_start,
                     'time_end': time_end,
                     'var': var}

                if not exists(out_filename, out_folder) or force:
                    out_filepath = os.path.join(out_folder, out_filename)
                    os.chdir(os.path.join(settings.DATA_FOLDER))
                    print('Extracting to %s...' % out_filename)

                    with open(os.path.join(BASE_DIR, 'R', 'Extract_historical_data.R'), 'r') as inputfile:
                        call(["R", "--no-save", "--args",
                              time_start, time_end, nc_filepath, var, out_filepath],
                             stdin=inputfile)
                else:
                    print('\nFile %s already exists, skipping preprocessing... (use force=True to override).' % out_filename)


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

    # Only consider 1 and 3 values as presence. 0 is too few jellyfishes.
    jellyfishes = ['Pel', 'Aur', 'Cot', 'Rhi', 'Chr', 'Aeq', 'Vel', 'Phys']
    for jellyfish in jellyfishes:
        obs_concated.ix[obs_concated[jellyfish] == 1, jellyfish] = 0
        obs_concated.ix[obs_concated[jellyfish] == 2, jellyfish] = 1
        obs_concated.ix[obs_concated[jellyfish] == 3, jellyfish] = 1

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

    if not exists(filename, folder) or force:
        os.chdir(settings.DATA_FOLDER)
        with open(os.path.join(BASE_DIR, 'R', 'Pnoctiluca_calibrate.R'), 'r') as inputfile:
            call(["R", "--no-save"], stdin=inputfile)
    else:
        print('\nFile %s already exists, skipping modelling... (use force=True to override).' % filename)


def calibrate(force=False):
    print("\n=== Calibrating model from historical data... ===")
    download_historical_data(DATASETS, force)
    extract_historical_data(DATASETS, force)
    preprocess_historical_data(DATASETS, force)
    calibrate_model(force)

if __name__ == "__main__":
    calibrate()
