"""
Run an R script to calibrate and make predictions, then upload the results to cartoDB.
"""

import os
import csv
from subprocess import call
from datetime import date, timedelta

from cartodb import CartoDBAPIKey, CartoDBException

from jellyrisk_forecaster.config import settings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def quote(value):
    return "'%s'" % value


def download_myocean_data(service, product,
                          time_start, time_end,
                          folder=None,
                          filename=None,
                          variables=None,
                          long_min=settings.LONG_MIN, long_max=settings.LONG_MAX,
                          lat_min=settings.LAT_MIN, lat_max=settings.LAT_MAX,
                          depth_min=settings.DEPTH_MIN, depth_max=settings.DEPTH_MAX,
                          username=settings.MYOCEAN_USERNAME,
                          password=settings.MYOCEAN_PASSWORD):
    if folder is None:
        folder = os.path.join(settings.DATA_FOLDER, 'MyOcean')
    if filename is None:
        filename = '%s.nc' % product

    call_stack = [
        settings.MOTU_CLIENT_PATH,
        '-u', settings.MYOCEAN_USERNAME,
        '-p', settings.MYOCEAN_PASSWORD,
        '-m', 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
        '-s', service, '-d', product,
        '-x', long_min, '-X', long_max,
        '-y', lat_min, '-Y', lat_max,
        '-z', depth_min, '-Z', depth_max,
        '-t', time_start, '-T', time_end,
        '-o', os.path.join(settings.DATA_FOLDER, 'MyOcean'),
        '-f', '%s.nc' % product
    ]
    if variables:
        for variable in variables:
            call_stack.append('-v')
            call_stack.append(variable)

    call(call_stack)


def download_historical_data():
    service = 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS'
    time_start = '2007-05-01'
    time_end = '2010-09-01'

    # temperature
    product = 'myov04-med-ingv-tem-rean-mm'
    download_myocean_data(
        service=service,
        product=product,
        time_start=time_start,
        time_end=time_end,
        filename='%s_2007-2010.nc' % product)

    # salinity
    product = 'myov04-med-ingv-sal-rean-mm'
    download_myocean_data(
        service=service,
        product=product,
        time_start=time_start,
        time_end=time_end,
        filename='%s_2007-2010.nc' % product)


# Download prediction data from MyOcean

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


def preprocess_historical_data():
    """Preprocess historical data from MyOcean data using R."""
    os.chdir(os.path.join(settings.DATA_FOLDER))
    with open(os.path.join(BASE_DIR, 'R', 'Compile_historical_data.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def preprocess_forecast_data():
    """Preprocess forecast environmental data from MyOcean using R."""
    os.chdir(os.path.join(settings.DATA_FOLDER))
    with open(os.path.join(BASE_DIR, 'R', 'ExtractData_MyOcean.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def calibrate_model():
    """Calibrate model using historical data."""
    os.chdir(settings.DATA_FOLDER)
    with open(os.path.join(BASE_DIR, 'R', 'Pnoctiluca_calibrate.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def predict_forecast():
    """Predict the presence of medusae using a previously calibrated model."""
    os.chdir(settings.DATA_FOLDER)
    with open(os.path.join(BASE_DIR, 'R', 'Pnoctiluca_predict.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def construct_query(limit_rows=settings.LIMIT_ROWS):
    values = []

    with open(os.path.join(settings.DATA_FOLDER, 'Pelagia.NoctilucaEF.csv'), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = ','.join([row['lon'], row['lat'], row['prob']])
            values.append('(' + value + ')')

    query = """
        INSERT INTO pred_pelagia_temperature_salinity_chlorophile (lon, lat, prob)
        VALUES %s;
        """ % ', '.join(values[:limit_rows])

    return query


def insert_data(query):
    """Connect to CartoDB and insert the data contained in tye query."""
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)

    try:
        print(cl.sql(query))
    except CartoDBException as e:
        print("some error ocurred", e)
        raise


def calibrate():
    download_historical_data()
    preprocess_historical_data()
    calibrate_model()


def predict():
    download_forecast_data()
    preprocess_forecast_data()
    predict_forecast()


def plot():
    query = construct_query()
    insert_data(query)


def main():
    calibrate()
    predict()
    plot()


if __name__ == "__main__":
    main()
