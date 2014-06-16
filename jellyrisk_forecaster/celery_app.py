from __future__ import absolute_import

from datetime import timedelta
from celery import Celery

app = Celery('jellyrisk_forecaster',
             broker='redis://localhost//',
             backend='redis',
             include=['jellyrisk_forecaster.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_TIMEZONE='Europe/Madrid',
    CELERYBEAT_SCHEDULE = {
        'oneshot-every-minute': {
            'task': 'jellyrisk_forecaster.tasks.main',
            'schedule': timedelta(minutes=60*24)
        },
    }
)

if __name__ == '__main__':
    app.start()