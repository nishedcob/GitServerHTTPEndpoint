#!/usr/bin/env bash
PORT_NUMBER=8020
command -v pipenv > /dev/null 2>&1
if [ $? -eq 0 ]; then
    #echo "pipenv detected";
    /usr/bin/env pipenv --venv
    if [ ! $? -eq 0 ]; then
        /usr/bin/env pipenv --three
    fi
    /usr/bin/env pipenv install
    /usr/bin/env pipenv run python manage.py runserver $PORT_NUMBER
else
    source activate.sh
    python manage.py runserver $PORT_NUMBER
    deactivate
fi
