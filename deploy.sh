#!/bin/bash
set +ex

if [ ! -e secrets.yaml ]; then
  gsutil cp gs://flask-boilerplate/secrets/secrets.yaml secrets.yaml
fi


gcloud app deploy --project flask-boilerplate
