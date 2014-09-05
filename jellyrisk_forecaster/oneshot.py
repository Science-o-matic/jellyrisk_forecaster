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


SERVICES_PRODUCTS_TIME = (
    ('http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_BIO_006_006-TDS', 'myov04-med-ogs-bio-an-fc', '12:00:00'),
    ('http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS', 'myov04-med-ingv-sal-an-fc', '00:00:00'),
    ('http://purl.org/myocean/ontology/service/database#MEDSEA_ANALYSIS_FORECAST_PHYS_006_001_a-TDS', 'myov04-med-ingv-tem-an-fc', '00:00:00'),
)


def quote(value):
    return "'%s'" % value


# Download prediction data from MyOcean

def download_data():
    # XXX: We can check if the data is already downloaded for desired day
    today = date.today()
    start = today + timedelta(days=1)   # data for tomorrow
    end = start

    for service, product, time in SERVICES_PRODUCTS_TIME:
        call([
            settings.MOTU_CLIENT_PATH,
            '-u', settings.MYOCEAN_USERNAME,
            '-p', settings.MYOCEAN_PASSWORD,
            '-m', 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
            '-s', service,
            '-d', product,
            '-x', '-2',
            '-X', '4',
            '-y', '38',
            '-Y', '44',
            '-t', '%s %s' % (start, time),
            '-T', '%s %s' % (end, time),
            '-z', '1.4721',
            '-Z', '4.58748',
            '-o', os.path.join(settings.DATA_FOLDER, 'MyOcean'),
            '-f', '%s.nc' % product,
        ])


# Extract varaibles data from MyOcean using R

def compile_historical_data():
    os.chdir(os.path.join(settings.DATA_FOLDER))
    with open(os.path.join(BASE_DIR, 'R', 'Compile_historical_data.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


# Extract prediction environmental data from MyOcean using R

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


def main():
    download_data()
    compile_historical_data()
    extract_prediction_data()
    calibrate_predict()
    query = construct_query()
    insert_data(query)

if __name__ == "__main__":
    main()
