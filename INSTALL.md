How to install
==============

In Ubuntu 10.04.4 LTS:

Install system requirements:

$ sudo apt-get install libgdal-dev libproj-dev

Add to /etc/apt/sources.list:

$ deb  http://ftp.cixug.es/CRAN/bin/linux/ubuntu lucid/

Add pubkey for this PPA:
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E084DAB9

Install biomod2 in R:
$ R
> install.packages('biomod2')
> install.packages('FNN')
> install.packages('raster')
> install.packages('rgdal')

Create a virtualenv, activate it and do:

$ pip install -r requirements.txt

Clone our motu-client-python fork modified to work in python 2.7.x:

git clone git@github.com:Science-o-matic/motu-client-python.git <path>

Copy the settings template file and modify to apply your settings:

$ cp jellyrisk_forecaster/settings.py.tmpl jellyrisk_forecaster/settings.py




To run the scripts, please set the environment variable JELLYRISK_SETTINGS_MODULE pointing to an accessible Python module with all the settings set:
 * CARTODB_API_KEY
 * CARTODB_DOMAIN
 * TEMP_FOLDER: folder to chdir to before executing the R script
 * DATA_FOLDER: folder with data files
 * Any celery-related config var. `app.config_from_object(JELLYRISK_SETTINGS_MODULE)' will be invoked.

Hint: Use virtualenv's postactivate and postdeactivate hooks.


Package to read netCDF files
============================
In R:

??	install.packages('ncdf')  # read netcdf files https://www.image.ucar.edu/GSP/Software/Netcdf/
