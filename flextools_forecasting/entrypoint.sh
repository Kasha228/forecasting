#!/bin/sh

python init_db.py

python save_swagger.py

exec gunicorn --bind 0.0.0.0:5002 --log-level 'debug' wsgi:app 
