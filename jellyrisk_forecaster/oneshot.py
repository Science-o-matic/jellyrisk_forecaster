"""
Run an R script to calibrate and make predictions, then upload the results to cartoDB.
"""

from jellyrisk_forecaster.calibrate import calibrate
from jellyrisk_forecaster.predict import predict
from jellyrisk_forecaster.plot import plot


if __name__ == "__main__":
    calibrate()
    predict()
    plot()
