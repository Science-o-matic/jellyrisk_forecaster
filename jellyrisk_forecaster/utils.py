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


def nc_to_csv(nc_filepath, out_filepath, beaches_path, var):
    """
    Extract variable data in the netcdf file for the given beaches.

    - nc_filepath: path to the netcdf file containing the variable data
    - out_filepath: path to the csv file to write to (will be created if doesn't exist)
    - beaches_path: path to the csv file with the coordinates of the beaches
      to extract the variable values for
    - var: name of the variable to extract the value for. Must coincide with
      the name of the variable in the netcdf file.
    """
    with open(os.path.join(BASE_DIR, 'R', 'Extract_historical_data.R'), 'r') as inputfile:
        call(["R", "--no-save", "--args", beaches_path, nc_filepath, var, out_filepath],
             stdin=inputfile)


def extract_historical_data(datasets, beaches_path, in_folder, out_folder, prefix='', force=False):
    """
    Extract variables values for all datasets and beaches, in CSV.

    If the output file is already present and force is False, skip preprocessing.

    - beaches_path: path to the csv file with the coordinates of the beaches
      to extract the variable values for
    - in_folder: folder where the netcdf files to extract are
    - out_folder: folder where to place the csv files
    - prefix: prefix for the netcdf and csv files
    - force: if True, don't generate the csv file if it is already present
    """
    create_if_not_exists(out_folder)

    for dataset in DATASETS:
        for time_start, time_end in zip(dataset['times_start'], dataset['times_end']):
            nc_filename = '%(prefix)s%(product)s_%(time_start)s_%(time_end)s.nc' % \
                {'prefix': prefix,
                 'product': dataset['product'],
                 'time_start': time_start,
                 'time_end': time_end}
            nc_filepath = os.path.join(in_folder, nc_filename)

            for var in dataset['vars']:
                out_filename = '%(prefix)s%(product)s_%(time_start)s_%(time_end)s-%(var)s.csv' % \
                    {'prefix': prefix,
                     'product': dataset['product'],
                     'time_start': time_start,
                     'time_end': time_end,
                     'var': var}

                if not exists(out_filename, out_folder) or force:
                    out_filepath = os.path.join(out_folder, out_filename)
                    os.chdir(os.path.join(settings.DATA_FOLDER))
                    print('Extracting to %s...' % out_filename)

                    nc_to_csv(nc_filepath, out_filepath, beaches_path, var)
                else:
                    print('\nFile %s already exists, skipping preprocessing... (use force=True to override).' % out_filename)
