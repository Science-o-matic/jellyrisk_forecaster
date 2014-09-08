import os
from subprocess import call

from jellyrisk_forecaster.utils import download_myocean_data
from jellyrisk_forecaster.config import settings, BASE_DIR


def download_historical_data():
    service = 'http://purl.org/myocean/ontology/service/database#MEDSEA_REANALYSIS_PHYS_006_004-TDS'
    time_start = '2007-05-01'
    time_end = '2010-09-01'

    # temperature
    product = 'myov04-med-ingv-tem-rean-mm'
    download_myocean_data(
        service=service,
        product=product,
        time_start=time_start,
        time_end=time_end,
        filename='%s_2007-2010.nc' % product)

    # salinity
    product = 'myov04-med-ingv-sal-rean-mm'
    download_myocean_data(
        service=service,
        product=product,
        time_start=time_start,
        time_end=time_end,
        filename='%s_2007-2010.nc' % product)


def preprocess_historical_data():
    """Preprocess historical data from MyOcean data using R."""
    os.chdir(os.path.join(settings.DATA_FOLDER))
    with open(os.path.join(BASE_DIR, 'R', 'Compile_historical_data.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def calibrate_model():
    """Calibrate model using historical data."""
    os.chdir(settings.DATA_FOLDER)
    with open(os.path.join(BASE_DIR, 'R', 'Pnoctiluca_calibrate.R'), 'r') as inputfile:
        call(["R", "--no-save"], stdin=inputfile)


def calibrate():
    download_historical_data()
    preprocess_historical_data()
    calibrate_model()

if __name__ == "__main__":
    calibrate()
