import os
import csv
from datetime import date, timedelta

from cartodb import CartoDBAPIKey, CartoDBException

from jellyrisk_forecaster.config import settings


def single_quote1(value):
    return "'%s'" % value


def truncate_table1(table=settings.CARTODB_TABLE1):
    query = 'TRUNCATE %s' % table
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY1, settings.CARTODB_DOMAIN1)
    cl.sql(query)


def delete_for_date1(target_date, table):
    print("\n=== Deleting existing data for date %s... ===" % target_date)
    date_formatted = target_date.strftime('%Y-%m-%d')
    query = "DELETE FROM %s WHERE date='%s'" % (table, date_formatted)
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY1, settings.CARTODB_DOMAIN1)
    cl.sql(query)


def construct_query1(target_date, clave, limit_rows=settings.LIMIT_ROWS):
    values = []
    folder = os.path.join(settings.DATA_FOLDER, 'Projections')
    filename = '{}EF-{}.csv'.format(clave, target_date.strftime('%Y-%m-%d'))

    with open(os.path.join(folder, filename), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lon = row['lon']
            lat = row['lat']
            prob = row['prob']
            probinf = row['probinf']
            probsup = row['probsup']
            date = row['date']
            the_geom = 'ST_SetSRID(ST_Point(%s, %s), 4326)' % (lon, lat)
            value = ', '.join([lon, lat, prob, probinf, probsup,
                               single_quote1(date), the_geom])
            values.append('(' + value + ')')

    query = 'INSERT INTO %s (lon, lat, prob, probinf, probsup, date, the_geom) VALUES %s;'  \
            % (settings.TUNEZ_DATA[clave]['carto'], ', '.join(values[:limit_rows]))
    return query


def insert_data1(query):
    """Connect to CartoDB and insert the data contained in tye query."""
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY1, settings.CARTODB_DOMAIN1)

    try:
        print(cl.sql(query))
    except CartoDBException as e:
        print("some error ocurred", e)
        raise


def plot_ahead1(days_ahead, delete_existing=True):
    today = date.today()
    target_dates = [today + timedelta(days=days) for days in range(0, days_ahead + 1)]

    for target_date in target_dates:
        plot1(target_date, delete_existing)


def plot1(target_date, delete_existing=True):
    print("\n=== Plotting for date %s... ===" % target_date)

    if delete_existing:
        for a in settings.TUNEZ_DATA:
            delete_for_date1(target_date, settings.TUNEZ_DATA[a]['carto'])
    for a in settings.TUNEZ_DATA:
	try:
       	    query = construct_query1(target_date, a)
            insert_data1(query)
	except:
	    pass

if __name__ == "__main__":
    plot_ahead1(days_ahead=2)
