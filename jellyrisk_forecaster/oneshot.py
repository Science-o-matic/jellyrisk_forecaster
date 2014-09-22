"""
Run an R script to calibrate and make predictions two days ahead, then upload
the results to cartoDB.
"""

from jellyrisk_forecaster.calibrate import calibrate
from jellyrisk_forecaster.predict import predict, predict_ahead
from jellyrisk_forecaster.plot import plot, plot_ahead


def predict_and_plot(target_date, force=False, delete_existing=True):
    """
    If force, data will be redownloaded and projections will be recalculated
    even if they already exist.

    If delete_existing, data already existing in the CartoDB table for the
    target_date will be deleted.
    """
    predict(target_date, force)
    plot(target_date, delete_existing)


def main():
    calibrate()
    predict_ahead(days_ahead=2)
    plot_ahead(days_ahead=2)


if __name__ == "__main__":
    main()
