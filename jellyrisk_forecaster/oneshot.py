"""
Run an R script to calibrate and make predictions, then upload the results to cartoDB.
"""

from jellyrisk_forecaster.calibrate import calibrate
from jellyrisk_forecaster.predict import predict
from jellyrisk_forecaster.plot import plot


def main():
    calibrate()
    predict(days_ahead=2)
    plot(days_ahead=2)

if __name__ == "__main__":
    main()
