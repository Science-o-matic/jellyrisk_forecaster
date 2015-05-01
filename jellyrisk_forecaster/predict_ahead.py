"""
Run an R script to calibrate and make predictions two days ahead, then upload
the results to cartoDB.
"""
from logging import config as logging_config
from jellyrisk_forecaster.calibrate import calibrate
from jellyrisk_forecaster.predict import predict_ahead
from jellyrisk_forecaster.plot import plot_ahead
from jellyrisk_forecaster.config import settings

logging_config.dictConfig(
{
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
        },
        'file': {
            'level':'DEBUG',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': '../logs/jellyrisk_forecaster.log',
            'when': 'W0',
            'backupCount': 4,
        },
        'mail': {
            'level':'ERROR',
            'class':'logging.handlers.SMTPHandler',
            'mailhost': settings.EMAIL_HOST,
            'fromaddr': settings.EMAIL_HOST_USER,
            'toaddrs': settings.EMAIL_TO,
            'subject': "[jellyrisk_forecaster] error log",
        },
    },
    'loggers': {
        'predict': {
            'handlers': ['default', 'file', 'mail'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
)


def main():
    calibrate()
    predict_ahead(days_ahead=2)
    plot_ahead(days_ahead=2)


if __name__ == "__main__":
    main()
