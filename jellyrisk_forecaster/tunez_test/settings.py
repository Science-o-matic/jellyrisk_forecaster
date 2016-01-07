import os
from datetime import timedelta

# Celery
BROKER_URL = 'redis://localhost//'
CELERY_RESULT_BACKEND = 'redis://'

CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TIMEZONE = 'Europe/Madrid'

CELERYBEAT_SCHEDULE = {
    'oneshot-every-minute': {
        'task': 'jellyrisk_forecaster.tasks.main',
        'schedule': timedelta(minutes=1)
    }
}

# SMTP
EMAIL_HOST = 'smtp.jellyrisk.eu'
EMAIL_TO = ("fuentesmartin@gmail.com")
EMAIL_HOST_USER = 'info@jellyrisk.eu'
EMAIL_HOST_PASSWORD = 'cmuMrxi5ffGg'

# CartoDB
CARTODB_API_KEY = '88a4a6d71419e6fe522a6302c8e9ace7004d8953'
CARTODB_DOMAIN = 'ygneo'
CARTODB_TABLE = 'pred_pelagia'

CARTODB_API_KEY1 = 'b2075e5a21d53f6e671996a1b97865c2546e67d3'
CARTODB_DOMAIN1 = 'som'
CARTODB_TABLE1 = 'tunez_today'

TUNEZ_DATA = {'Rpulmo': {'carto': 'tunez_rpulmo'} , 'Vvelella': {'carto': 'tunez_vvelella'}, 'Aaurita': {'carto': 'tunez_today'}} 
#TUNEZ_DATA = {'Vvelella': {'carto': 'tunez_vvelella'}} 

# Folders
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, 'data')

MYOCEAN_USERNAME = 'llopezcastillo'
MYOCEAN_PASSWORD = 'zJhqbjpwM'
#MYOCEAN_USERNAME = 'mfuentes'
#MYOCEAN_PASSWORD = 'y4stuAEE'
##MYOCEAN_PASSWORD = 'pdtkQqUA'

MOTU_CLIENT_PATH = '/home/jellyrisk/motu-client-python/motu-client.py'
