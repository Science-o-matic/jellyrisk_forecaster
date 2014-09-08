import os
import csv

from cartodb import CartoDBAPIKey, CartoDBException

from jellyrisk_forecaster.config import settings


def construct_query(limit_rows=settings.LIMIT_ROWS):
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


def insert_data(query):
    """Connect to CartoDB and insert the data contained in tye query."""
    cl = CartoDBAPIKey(settings.CARTODB_API_KEY, settings.CARTODB_DOMAIN)

    try:
        print(cl.sql(query))
    except CartoDBException as e:
        print("some error ocurred", e)
        raise


def plot():
    query = construct_query()
    insert_data(query)


if __name__ == "__main__":
    plot()
