from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account  #

import os
import yaml

from .app import create_app

key_path = "secret.json"
credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path)
credentials2 = service_account.Credentials.from_service_account_file(key_path)

config = {
    "GCS_ROOT_PATH": os.environ["GCS_ROOT_PATH"],
    "DATASTORE_PROJECT": "flask-template",
    "GCP_CREDENTIALS": credentials,
    "GCP_CREDENTIALS_2": credentials2,
    "SECRET_KEY": os.environ["SECRET_KEY"],
}

if os.environ.get("DEV_OVERRIDE_USER"):
    config["DEV_OVERRIDE_USER"] = os.environ["DEV_OVERRIDE_USER"]

app = create_app(config)
