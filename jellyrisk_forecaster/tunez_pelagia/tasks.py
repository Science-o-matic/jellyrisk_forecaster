from jellyrisk_forecaster import oneshot
from jellyrisk_forecaster.celery_app import app

@app.task
def main():
    oneshot.main()