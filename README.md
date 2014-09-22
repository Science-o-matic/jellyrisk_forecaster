jellyrisk_forecaster
====================

Python app to build jellyfishes risk forecastings.

It works calibrating an ensemble of models using historical data and then using this model
to predict the presence of jellyfishes in future dates.

The climatological and biological data, both historical and predictions, is downloaded
from MyOcean. The historical jellyfish presence data is provided by the Maritimal Sciences
Institute (ICM).

Data processing and modelling is performed using R and the package biomod2. The rest of the
system is written in Python.
