"""
Run an R script to calibrate and make predictions, then upload the results to cartoDB.
"""

import os
import csv
import shutil
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


### Create temporal folder for the R script output files and copy data to it

def initialize():
    if not os.path.exists(settings.TEMP_FOLDER):
        os.makedirs(settings.TEMP_FOLDER)
    shutil.copytree(settings.DATA_FOLDER, os.path.join(settings.TEMP_FOLDER, 'data'))


### Download prediction data from MyOcean

def download_data():
    today = date.today()
    start = today + timedelta(days=1)
    end = start

    for service, product, time in SERVICES_PRODUCTS_TIME:
        call([
            settings.MOTU_CLIENT_PATH,
            '-u', settings.MYOCEAN_USERNAME,
            '-p', settings.MYOCEAN_PASSWORD,
            '-m', 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
            '-s', service,
            '-d', product,
            '-x', '-6',
            '-X', '36.25',
            '-y', '30.1875',
            '-Y', '45.9375',
            '-t', '%s %s' % (start, time),
            '-T', '%s %s' % (end, time),
            '-z', '1.4721',
            '-Z', '4.58748',
            '-o', settings.TEMP_FOLDER,
            '-f', '%s.nc' % product,
        ])


### Extract varaibles data from MyOcean using R

def extract_data():
    os.chdir(settings.TEMP_FOLDER)
    with open(os.path.join(BASE_DIR, 'R/ExtractData_myocean.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


### Call R script

def calibrate_predict():
    os.chdir(settings.TEMP_FOLDER)
    with open(os.path.join(BASE_DIR, 'R/Pnoctiuca_myocean_calibrate_predict.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


### Open resulting CSV file and construct query

def construct_query(limit_rows=LIMIT_ROWS):
    values = []

    with open(os.path.join(settings.TEMP_FOLDER, 'Pelagia.NoctilucaEF.csv'), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = ','.join([row['lon'], row['lat'], row['prob']])
            values.append('(' + value + ')')

    query = """
        INSERT INTO pred_pelagia (lon, lat, prob)
        VALUES %s;
        """ % ', '.join(values[:limit_rows])

    return query


### Connect to CartoDB and insert data

def insert_data(query):
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)

    try:
       print cl.sql(query)
    except CartoDBException as e:
       print ("some error ocurred", e)
       raise


### Clean up

def cleanup():
    if os.path.exists(settings.TEMP_FOLDER):
        shutil.rmtree(settings.TEMP_FOLDER)


def main():
    cleanup()
    initialize()
    download_data()
    extract_data()
    calibrate_predict()
    query = construct_query()
    insert_data(query)
    cleanup()

if __name__ == "__main__":
    main()
