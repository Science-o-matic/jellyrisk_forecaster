import sys
from datetime import datetime

from jellyrisk_forecaster.predict import predict
from jellyrisk_forecaster.plot import plot


def predict_and_plot(target_date, force=False, delete_existing=True):
    """
    If force, data will be redownloaded and projections will be recalculated
    even if they already exist.

    If delete_existing, data already existing in the CartoDB table for the
    target_date will be deleted.
    """
    predict(target_date, force)
    plot(target_date, delete_existing)


if __name__ == "__main__":
    date_string = sys.argv[1]
    target_date = datetime.strptime(date_string, "%Y-%m-%d").date()
    predict_and_plot(target_date)
