import csv
from cartodb import CartoDBAPIKey, CartoDBException

from config import API_KEY, cartodb_domain


def quote(value):
    return "'%s'" % value

values = []

with open('../data/pred_pelagia.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        value = ','.join([row['long'], row['lat'], row['pelagia'], quote(row['the_geom'])])
        values.append('(' + value + ')')


cl = CartoDBAPIKey(API_KEY, cartodb_domain)

query = """
    INSERT INTO pred_pelagia (long, lat, pelagia, the_geom) 
    VALUES %s;
    """ % ', '.join(values)


try:
   print cl.sql(query)
except CartoDBException as e:
   print ("some error ocurred", e)