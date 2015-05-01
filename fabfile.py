from fabric.api import task, roles, env, cd, run

env.forward_agent = True

env.roledefs = {
    "guachiman": ["jellyrisk@guachiman.science-o-matic.com"],
}

@roles("guachiman")
@task
def release(branch="master"):
    with cd("/home/jellyrisk/jellyrisk_forecaster"):
        run('git fetch --all')
        run('git checkout {}'.format(branch))
        run('git reset --hard origin/{}'.format(branch))


@roles("guachiman")
@task
def runpredict():
    with cd("/home/jellyrisk/jellyrisk_forecaster/jellyrisk_forecaster"):
        run(". /home/jellyrisk/.virtualenvs/jellyrisk_forecaster/bin/activate; python predict_ahead.py")
