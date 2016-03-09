import csv
import os

from cartodb import CartoDBAPIKey, CartoDBException


API_KEY = os.environ.get("CARTODB_API_KEY")
DOMAIN = os.environ.get("CARTODB_DOMAIN")

if not API_KEY or not DOMAIN:
    raise EnvironmentError('Please set both CARTODB_API_KEY and CARTODB_DOMAIN environment variables.')


def quote(value):
    return "'%s'" % value

values = []

with open('../data/pred_pelagia.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        value = ','.join([row['long'], row['lat'], row['pelagia'], quote(row['the_geom'])])
        values.append('(' + value + ')')


cl = CartoDBAPIKey(API_KEY, DOMAIN)

query = """
    INSERT INTO pred_pelagia (long, lat, pelagia, the_geom) 
    VALUES %s;
    """ % ', '.join(values)


try:
   print cl.sql(query)
except CartoDBException as e:
   print ("some error ocurred", e)