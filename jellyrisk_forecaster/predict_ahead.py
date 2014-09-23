"""
Run an R script to calibrate and make predictions two days ahead, then upload
the results to cartoDB.
"""

from jellyrisk_forecaster.calibrate import calibrate
from jellyrisk_forecaster.predict import predict_ahead
from jellyrisk_forecaster.plot import plot_ahead


def main():
    calibrate()
    predict_ahead(days_ahead=2)
    plot_ahead(days_ahead=2)


if __name__ == "__main__":
    main()
