"""
Run an R script to calibrate and make predictions, then upload the results to cartoDB.
"""

import os
import csv
import shutil
from subprocess import call

from cartodb import CartoDBAPIKey, CartoDBException

from jellyrisk_forecaster.config import settings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LIMIT_ROWS = getattr(settings, 'SETTINGS_LIMIT_ROWS', 15000)

def quote(value):
    return "'%s'" % value



### 0. create temporal folder for the R script output files and copy data to it

def initialize():
    if not os.path.exists(settings.TEMP_FOLDER):
        os.makedirs(settings.TEMP_FOLDER)
    shutil.copytree(settings.DATA_FOLDER, os.path.join(settings.TEMP_FOLDER, 'data'))


### 1. Call R script

def calibrate_predict():
    os.chdir(settings.TEMP_FOLDER)
    with open(os.path.join(BASE_DIR, 'R/Pnoctiuca_calibrate_predict.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


### 2. Open resulting CSV file and construct query

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


### 3. Connect to CartoDB and insert data

def insert_data(query):
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)

    try:
       print cl.sql(query)
    except CartoDBException as e:
       print ("some error ocurred", e)
       raise


### -1: Clean up

def cleanup():
    shutil.rmtree(settings.TEMP_FOLDER)


def main():
    initialize()
    calibrate_predict()
    query = construct_query()
    insert_data(query)
    cleanup()

if __name__ == "__main__":
    main()
