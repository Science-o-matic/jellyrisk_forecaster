import os
from subprocess import call

from jellyrisk_forecaster.utils import exists
from jellyrisk_forecaster.utils import download_myocean_data, create_if_not_exists
from jellyrisk_forecaster.config import settings, BASE_DIR


def download_historical_data(force=False):
    time_start = '2007-05-01'
    time_end = '2010-09-01'
    folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical')
    create_if_not_exists(folder)
    datasets = [
        {   # chlorophile, nitrate, phosphate, oxygen...
            'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS',
            'product': 'myov04-med-ogs-bio-an-fc',
            'time': '12:00:00',
        },
        {   # salinity
            'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
            'product': 'myov05-med-ingv-sal-an-fc-dm',
            'time': '00:00:00'
        },
        {   # temperature
            'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
            'product': 'myov05-med-ingv-tem-an-fc-dm',
            'time': '00:00:00'
        },
        {   # temperature
            'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
            'product': 'myov05-med-ingv-cur-an-fc-dm',
            'time': '00:00:00',
            'variables': ['vozocrtx', 'vomecrty']
        }
    ]

 

    for dataset in datasets:
        filename = '%s_2007-2010.nc' % dataset['product']
        if not exists(filename, folder) or force:
            download_myocean_data(
                service=dataset['service'],
                product=dataset['product'],
                time_start=time_start,
                time_end=time_end,
                folder=folder,
                filename=filename)
        else:
            print('File %s already exists, skipping download... (use force=True to override).' % filename)


def preprocess_historical_data(force=False):
    """Preprocess historical data from MyOcean data using R.

    If the output file is already present and force is False, skip preprocessing.
    """
    folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Historical')
    filename = 'historical-data-by-beach-2007-2010.csv'
    create_if_not_exists(folder)

    if not exists(filename, folder) or force:
        os.chdir(os.path.join(settings.DATA_FOLDER))
        with open(os.path.join(BASE_DIR, 'R', 'Compile_historical_data.R'), 'r') as inputfile:
            call(["R", "--no-save"], stdin=inputfile)
    else:
        print('\nFile %s already exists, skipping preprocessing... (use force=True to override).' % filename)


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
    download_historical_data(force)
    preprocess_historical_data(force)
    calibrate_model(force)

if __name__ == "__main__":
    calibrate()
