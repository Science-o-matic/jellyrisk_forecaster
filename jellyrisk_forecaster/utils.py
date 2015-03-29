import os
import time
from subprocess import check_call, CalledProcessError

from jellyrisk_forecaster.config import settings


def exists(filename, folder):
    """Return true if file with the given name exists in the folder."""
    return os.path.exists(os.path.join(folder, filename))


def create_if_not_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def download_myocean_data(service, product,
                          time_start, time_end,
                          module=None,
                          folder=None,
                          filename=None,
                          variables=None,
                          long_min=settings.LONG_MIN, long_max=settings.LONG_MAX,
                          lat_min=settings.LAT_MIN, lat_max=settings.LAT_MAX,
                          depth_min=settings.DEPTH_MIN, depth_max=settings.DEPTH_MAX,
                          username=settings.MYOCEAN_USERNAME,
                          password=settings.MYOCEAN_PASSWORD):

    if folder is None:
        folder = os.path.join(settings.DATA_FOLDER, 'MyOcean')
    if filename is None:
        filename = '%s.nc' % product
    if module is None:
        module = 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu'

    call_stack = [
        settings.MOTU_CLIENT_PATH,
        '-u', settings.MYOCEAN_USERNAME,
        '-p', settings.MYOCEAN_PASSWORD,
        '-m', module,
        '-s', service, '-d', product,
        '-x', long_min, '-X', long_max,
        '-y', lat_min, '-Y', lat_max,
        '-z', depth_min, '-Z', depth_max,
        '-t', time_start, '-T', time_end,
        '-o', folder,
        '-f', filename
    ]
    if variables:
        for variable in variables:
            call_stack.append('-v')
            call_stack.append(variable)

    tries = 0
    while(tries < settings.MOTU_CLIENT_RETRIES):
        try:
            check_call(call_stack)
            break
        except CalledProcessError:
            tries += 1
            time.sleep(settings.MOTU_CLIENT_RETRY_DELAY_SECS)

    if tries == settings.MOTU_CLIENT_RETRIES:
        message = "Maximun tries=%i exceeded trying to donwload %s!" % (
                settings.MOTU_CLIENT_RETRIES, filename)
        print message
        raise Exception(message)
    print(call_stack)
