import os
from subprocess import call
from datetime import date, timedelta

from jellyrisk_forecaster.utils import download_myocean_data
from jellyrisk_forecaster.config import settings, BASE_DIR


def download_forecast_data(start_date=None, end_date=None):
    # XXX: We can check if the data is already downloaded for desired day
    today = date.today()
    if start_date is None:
        start_date = today + timedelta(days=1)  # data for tomorrow
    if end_date is None:
        end_date = start_date

    # chlorophile, nitrate, phosphate, oxygen...
    download_myocean_data(
        service='http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS',
        product='myov04-med-ogs-bio-an-fc',
        time_start='%s %s' % (start_date, '12:00:00'),
        time_end='%s %s' % (end_date, '12:00:00'))

    # salinity
    download_myocean_data(
        service='http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        product='myov04-med-ingv-sal-an-fc',
        time_start='%s %s' % (start_date, '00:00:00'),
        time_end='%s %s' % (end_date, '00:00:00'))
    # temperature
    download_myocean_data(
        service='http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS',
        product='myov04-med-ingv-tem-an-fc',
        time_start='%s %s' % (start_date, '00:00:00'),
        time_end='%s %s' % (end_date, '00:00:00'))


def preprocess_forecast_data():
    """Preprocess forecast environmental data from MyOcean using R."""
    os.chdir(os.path.join(settings.DATA_FOLDER))
    with open(os.path.join(BASE_DIR, 'R', 'ExtractData_MyOcean.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def predict_forecast():
    """Predict the presence of medusae using a previously calibrated model."""
    os.chdir(settings.DATA_FOLDER)
    with open(os.path.join(BASE_DIR, 'R', 'Pnoctiluca_predict.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def predict():
    download_forecast_data()
    preprocess_forecast_data()
    predict_forecast()


if __name__ == "__main__":
    predict()
