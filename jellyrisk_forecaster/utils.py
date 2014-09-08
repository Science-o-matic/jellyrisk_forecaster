import os
from subprocess import call

from jellyrisk_forecaster.config import settings


def download_myocean_data(service, product,
                          time_start, time_end,
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

    call_stack = [
        settings.MOTU_CLIENT_PATH,
        '-u', settings.MYOCEAN_USERNAME,
        '-p', settings.MYOCEAN_PASSWORD,
        '-m', 'http://gnoodap.bo.ingv.it/mis-gateway-servlet/Motu',
        '-s', service, '-d', product,
        '-x', long_min, '-X', long_max,
        '-y', lat_min, '-Y', lat_max,
        '-z', depth_min, '-Z', depth_max,
        '-t', time_start, '-T', time_end,
        '-o', os.path.join(settings.DATA_FOLDER, 'MyOcean'),
        '-f', '%s.nc' % product
    ]
    if variables:
        for variable in variables:
            call_stack.append('-v')
            call_stack.append(variable)

    call(call_stack)
