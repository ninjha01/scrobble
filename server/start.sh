#!/bin/bash
if [ ! -e secret.yaml ]; then
    gsutil cp gs://scrobble_secrets/secret.yaml secret.yaml
fi
if [ ! -e secret.json ]; then
    gsutil cp gs://scrobble_secrets/secret.json secret.json
fi

export FLASK_DEBUG=TRUE
export FLASK_APP=main.py
export OAUTHLIB_INSECURE_TRANSPORT=1
export DEV_OVERRIDE_USER="${whoami}@gmail.com"

export GCS_ROOT_PATH='gs://scrobble/uploads'
export GOOGLE_APPLICATION_CREDENTIALS="./secret.json"
echo "WARNING: Overriding user in development mode. All requests will be on behalf of $DEV_OVERRIDE_USER"

flask run 
