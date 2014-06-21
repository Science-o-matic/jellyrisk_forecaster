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
TEMPFOLDER = os.path.join(BASE_DIR, 'tmp')


def quote(value):
    return "'%s'" % value



### 0. create temporal folder for the R script output files

def initialize():
    if not os.path.exists(TEMPFOLDER):
        os.makedirs(TEMPFOLDER)


### 1. Call R script

def calibrate_predict():
    os.chdir(TEMPFOLDER)
    with open(os.path.join(BASE_DIR, 'R/GuloGulo_calibrate_predict.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


### 2. Open resulting CSV file and construct query

def construct_query():
    values = []

    with open(os.path.join(TEMPFOLDER, 'GuloGuloEF.csv'), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = ','.join([row['lon'], row['lat'], row['prob']])
            values.append('(' + value + ')')

    query = """
        INSERT INTO guloguloout (lon, lat, prob) 
        VALUES %s;
        """ % ', '.join(values)

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
    shutil.rmtree(TEMPFOLDER)


def main():
    initialize()
    calibrate_predict()
    query = construct_query()
    insert_data(query)
    cleanup()

if __name__ == "__main__":
    main()
