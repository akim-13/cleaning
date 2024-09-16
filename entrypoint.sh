#!/bin/bash

# Exit immediately if any command fails.
set -e

python manage.py makemigrations 
python manage.py migrate 
python manage.py collectstatic --noinput

# Start the server with a debugger attached and watch for any file changes to auto-restart.
watchmedo auto-restart --recursive -- \
    python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 \
    /usr/local/bin/daphne -b 0.0.0.0 -p 8000 cleaning_website.asgi:application

# Use this instead to first wait for debugger to attach before executing anything.
#python -Xfrozen_modules=off -m debugpy --listen 0.0.0.0:5678 --wait-for-client /usr/local/bin/daphne -b 0.0.0.0 -p 8000 cleaning_website.asgi:application
