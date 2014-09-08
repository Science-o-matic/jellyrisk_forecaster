import os
from subprocess import call
from datetime import date, timedelta

from jellyrisk_forecaster.utils import exists, download_myocean_data
from jellyrisk_forecaster.config import settings, BASE_DIR

DATE_FORMAT = '%Y-%m-%d'


def download_forecast_data(target_date, force=False):
    """Download forecast data for the given target date.

    If force is False, data is only downloaded if it doesn't already exist.
    """

    start_date = end_date = target_date
    target_date_formatted = start_date.strftime(DATE_FORMAT)
    folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Forecast')

    datasets = [
        {   # chlorophile, nitrate, phosphate, oxygen...
            'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS',
            'product': 'myov04-med-ogs-bio-an-fc',
            'time': '12:00:00'
        },
        {   # salinity
            'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
            'product': 'myov04-med-ingv-sal-an-fc',
            'time': '00:00:00'
        },
        {   # temperature
            'service': 'http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
            'product': 'myov04-med-ingv-tem-an-fc',
            'time': '00:00:00'
        }
    ]

    for dataset in datasets:
        filename = '%s-%s.nc' % (dataset['product'], target_date_formatted)
        if not exists(filename, folder) or force:
            download_myocean_data(
                service=dataset['service'],
                product=dataset['product'],
                time_start='%s %s' % (start_date, dataset['time']),
                time_end='%s %s' % (end_date, dataset['time']),
                folder=folder,
                filename=filename)
        else:
            print('File %s already exists, skipping download... (use force=True to override).' % filename)


def preprocess_forecast_data(target_date, force=False):
    """Preprocess forecast environmental data from MyOcean using R.

    If force is False, it is only preprocessed if the output file doesn't already exist.
    """
    filename = 'Forecast_Env-%s.csv' % target_date.strftime(DATE_FORMAT)
    folder = os.path.join(settings.DATA_FOLDER, 'MyOcean', 'Forecast')

    if not exists(filename, folder) or force:
        os.chdir(os.path.join(settings.DATA_FOLDER))
        with open(os.path.join(BASE_DIR, 'R', 'ExtractData_MyOcean.R'), 'r') as inputfile:
            call(["R", "--no-save",
                  "--args", target_date.strftime(DATE_FORMAT)], stdin=inputfile)
    else:
        print('\nFile %s already exists, skipping preprocessing... (use force=True to override).' % filename)


def predict_forecast(target_date, force=False):
    """Predict the presence of medusae using a previously calibrated model.

    If force is False, it is only predicted the output file doesn't already exist.
    """
    filename = 'PelagiaNoctilucaEF-%s.csv' % target_date.strftime(DATE_FORMAT)
    folder = os.path.join(settings.DATA_FOLDER, 'Projections')

    if not exists(filename, folder) or force:
        os.chdir(settings.DATA_FOLDER)
        with open(os.path.join(BASE_DIR, 'R', 'Pnoctiluca_predict.R'), 'r') as inputfile:
            call(["R", "--no-save",
                  "--args", target_date.strftime(DATE_FORMAT)], stdin=inputfile)
    else:
        print('\nFile %s already exists, skipping prediction... (use force=True to override).' % filename)


def predict(days_ahead=2, force=False):
    today = date.today()
    target_dates = [today + timedelta(days=days) for days in range(1, days_ahead + 1)]

    for target_date in target_dates:
        print("\n=== Predicting for date %s... ===" % target_date)
        download_forecast_data(target_date, force)
        preprocess_forecast_data(target_date, force)
        predict_forecast(target_date, force)


if __name__ == "__main__":
    predict()
