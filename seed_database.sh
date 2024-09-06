#!/bin/bash

rm db.sqlite3
rm -rf ./npoapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations npoapi
python3 manage.py migrate npoapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens

