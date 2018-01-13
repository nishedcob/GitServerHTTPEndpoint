#!/usr/bin/env bash
PORT_NUMBER="8020"
PIPENV_COMMAND="pipenv"
ENV_COMMAND="/usr/bin/env"
DJANGO_COMMAND="python manage.py runserver $PORT_NUMBER"
command -v $PIPENV_COMMAND
if [ $? -eq 0 ]; then
    PIPENV_COMMAND="$ENV_COMMAND $PIPENV_COMMAND"
    $PIPENV_COMMAND --venv
    if [ ! $? -eq 0 ]; then
        $PIPENV_COMMAND --three
    fi
    $PIPENV_COMMAND install
    $PIPENV_COMMAND run $DJANGO_COMMAND
else
    source activate.sh
    $DJANGO_COMMAND
    deactivate
fi
