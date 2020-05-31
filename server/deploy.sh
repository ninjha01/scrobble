#!/bin/bash
set +ex
if [ ! -e secret.json ]; then
    gsutil cp gs://scrobble_secrets/secret.json secret.json
fi

if [ ! -e secret.yaml ]; then
    gsutil cp gs://scrobble_secrets/secret.yaml secret.yaml
fi

gcloud app deploy --project scrobble
