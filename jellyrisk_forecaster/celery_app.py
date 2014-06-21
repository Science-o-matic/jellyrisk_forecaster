from __future__ import absolute_import

from celery import Celery
from jellyrisk_forecaster.config import settings


app = Celery('jellyrisk_forecaster',
             include=['jellyrisk_forecaster.tasks'])

app.config_from_object(settings)

if __name__ == '__main__':
    app.start()
