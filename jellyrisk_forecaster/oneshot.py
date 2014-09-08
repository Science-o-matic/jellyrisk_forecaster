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
LIMIT_ROWS = getattr(settings, 'SETTINGS_LIMIT_ROWS', 15000)

LONG_MIN = '-2'
LONG_MAX = '4'
LAT_MIN = '38'
LAT_MAX = '44'
DEPTH_MIN = '1.4721'
DEPTH_MAX = '4.58748'


def quote(value):
    return "'%s'" % value


def download_myocean_data(service, product,
                          time_start, time_end,
                          folder=None,
                          filename=None,
                          variables=None,
                          long_min=LONG_MIN, long_max=LONG_MAX,
                          lat_min=LAT_MIN, lat_max=LAT_MAX,
                          depth_min=DEPTH_MIN, depth_max=DEPTH_MAX,
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
        start = today + timedelta(days=1)  # data for tomorrow
    if end_date is None:
        end_date = start

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


# Preprocess historical data from MyOcean data using R

def compile_historical_data():
    os.chdir(os.path.join(settings.DATA_FOLDER))
    with open(os.path.join(BASE_DIR, 'R', 'Compile_historical_data.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


# Preprocess forecast environmental data from MyOcean using R

def extract_prediction_data():
    os.chdir(os.path.join(settings.DATA_FOLDER))
    with open(os.path.join(BASE_DIR, 'R', 'ExtractData_MyOcean.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


# Call R script

def calibrate_predict():
    os.chdir(settings.DATA_FOLDER)
    with open(os.path.join(BASE_DIR, 'R', 'Pnoctiuca_myocean_calibrate_predict.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


# Open resulting CSV file and construct query

def construct_query(limit_rows=LIMIT_ROWS):
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


# Connect to CartoDB and insert data

def insert_data(query):
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)

    try:
        print(cl.sql(query))
    except CartoDBException as e:
        print("some error ocurred", e)
        raise


def download_data():
    download_historical_data()
    download_forecast_data()


def preprocess_data():
    compile_historical_data()
    extract_prediction_data()


def main():
    download_data()
    preprocess_data()
    calibrate_predict()
    query = construct_query()
    insert_data(query)

if __name__ == "__main__":
    main()
