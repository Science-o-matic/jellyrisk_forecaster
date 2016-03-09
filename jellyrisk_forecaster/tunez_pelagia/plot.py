import os
import csv
from datetime import date, timedelta

from cartodb import CartoDBAPIKey, CartoDBException

from jellyrisk_forecaster.config import settings


def single_quote(value):
    return "'%s'" % value


def truncate_table(table=settings.CARTODB_TABLE):
    query = 'TRUNCATE %s' % table
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)
    cl.sql(query)


def delete_for_date(target_date, table=settings.CARTODB_TABLE):
    print("\n=== Deleting existing data for date %s... ===" % target_date)
    date_formatted = target_date.strftime('%Y-%m-%d')
    query = "DELETE FROM %s WHERE date='%s'" % (table, date_formatted)
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)
    cl.sql(query)


def construct_query(target_date, limit_rows=settings.LIMIT_ROWS):
    values = []
    folder = os.path.join(settings.DATA_FOLDER, 'Projections')
    filename = 'PelagiaNoctilucaEF-%s.csv' % target_date.strftime('%Y-%m-%d')

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
                               single_quote(date), the_geom])
            values.append('(' + value + ')')

    query = 'INSERT INTO %s (lon, lat, prob, probinf, probsup, date, the_geom) VALUES %s;'  \
            % (settings.CARTODB_TABLE, ', '.join(values[:limit_rows]))
    return query


def insert_data(query):
    """Connect to CartoDB and insert the data contained in tye query."""
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)

    try:
        print(cl.sql(query))
    except CartoDBException as e:
        print("some error ocurred", e)
        raise


def plot_ahead(days_ahead, delete_existing=True):
    today = date.today()
    target_dates = [today + timedelta(days=days) for days in range(0, days_ahead + 1)]

    for target_date in target_dates:
        plot(target_date, delete_existing)


def plot(target_date, delete_existing=True):
    print("\n=== Plotting for date %s... ===" % target_date)

    if delete_existing:
        delete_for_date(target_date)

    query = construct_query(target_date)
    insert_data(query)


if __name__ == "__main__":
    plot_ahead(days_ahead=2)
