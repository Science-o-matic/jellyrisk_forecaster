How to install
==============

In Ubuntu Linux:
	
	sudo apt-get install libgdal-dev libproj-dev


Create a virtualenv, activate it and do:

	pip install -r requirements.txt

In R:

	install.packages('biomod2')

	install.packages('rgdal')

To run the scripts, please set the environment variables CARTODB_API_KEY and CARTODB_DOMAIN. (Hint: Use virtualenv's postactivate and postdeactivate hooks.)


Package to read netCDF files
============================
In R:

	install.packages('ncdf')  # read netcdf files https://www.image.ucar.edu/GSP/Software/Netcdf/
