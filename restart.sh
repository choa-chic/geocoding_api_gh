#!/bin/bash

cd /data/jmb_dev/geocoding_api

# clear the logs
cat /dev/null > logs/app/app.log
cat /dev/null > logs/gunicorn/access.log
cat /dev/null > logs/gunicorn/error.log


docker build -t geocoder-api .

docker run -it -d --replace --name gs \
    -v $(pwd)/logs/gunicorn:/var/log/gunicorn \
    -v $(pwd)/logs/app:/app/log \
    -p 9080:9080 localhost/geocoder-api

# cd testing
# python test_csv_method.py