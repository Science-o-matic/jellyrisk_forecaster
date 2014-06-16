How to install
==============

In Ubuntu Linux:
	
	sudo apt-get install libgdal-dev libproj-dev


Create a virtualenv, activate it and do:

	pip install -r requirements.txt

In R:

	install.packages('biomod2')

	install.packages('rgdal')

To run the scripts, please set the environment variable JELLYRISK_SETTINGS_MODULE pointing to an accessible Python module with all the settings set:
 * CARTODB_API_KEY
 * CARTODB_DOMAIN
 * Any celery-related config var. `app.config_from_object(JELLYRISK_SETTINGS_MODULE)' will be invoked.

Hint: Use virtualenv's postactivate and postdeactivate hooks.


Package to read netCDF files
============================
In R:

	install.packages('ncdf')  # read netcdf files https://www.image.ucar.edu/GSP/Software/Netcdf/
