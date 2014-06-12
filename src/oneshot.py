"""
Run an R script to calibrate and make predictions, then upload the results to cartoDB.
"""

import os
import csv
import shutil
from subprocess import call

from cartodb import CartoDBAPIKey, CartoDBException

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
API_KEY = os.environ.get("CARTODB_API_KEY")
DOMAIN = os.environ.get("CARTODB_DOMAIN")

if not API_KEY or not DOMAIN:
    raise EnvironmentError('Please set both CARTODB_API_KEY and CARTODB_DOMAIN environment variables.')

def quote(value):
    return "'%s'" % value


# create temporal folder for the R script output files
tempFolder = os.path.join(BASE_DIR, 'tmp')
if not os.path.exists(tempFolder):
    os.makedirs(tempFolder)


### 1. Call R script

with open(os.path.join(BASE_DIR, 'R/GuloGulo_calibrate_predict.R'), 'r') as inputfile:
    call(["R", "--no-save"], stdin=inputfile)


### 2. Open resulting CSV file and construct query

values = []

with open(os.path.join(tempFolder, 'GuloGuloEF.csv'), 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        value = ','.join([row['lon'], row['lat'], row['prob']])
        values.append('(' + value + ')')

query = """
    INSERT INTO guloguloout (lon, lat, prob) 
    VALUES %s;
    """ % ', '.join(values)


### 3. Connect to CartoDB and insert data

cl = CartoDBAPIKey(API_KEY, DOMAIN)

try:
   print cl.sql(query)
except CartoDBException as e:
   print ("some error ocurred", e)


### -1: Clean up

shutil.rmtree(tempFolder)