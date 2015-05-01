from fabric.api import task, roles, env, cd, run

env.forward_agent = True

env.roledefs = {
    "guachiman": ["jellyrisk@guachiman.science-o-matic.com"],
}

@roles("guachiman")
@task
def release():
    with cd("/home/jellyrisk/jellyrisk_forecaster"):
        run('git fetch --all')
        run('git checkout master')
        run('git reset --hard origin/master')


@roles("guachiman")
@task
def runpredict():
    with cd("/home/jellyrisk/jellyrisk_forecaster/jellyrisk_forecaster"):
        run(". /home/jellyrisk/.virtualenvs/jellyrisk_forecaster/bin/activate; python predict_ahead.py")
