#!/bin/bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --indent 2 > db.json
echo "Data dumped to db.json"
