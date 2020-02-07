from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account  #

import os
import yaml

from cdsprojects.app import create_app

key_path = "secret.json"
credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path)
credentials2 = service_account.Credentials.from_service_account_file(key_path)

with open("./secrets.yaml") as f:
    secrets = yaml.load(f, Loader=yaml.SafeLoader)["env_variables"]

config = {
    "GOOGLE_CLIENT_ID": secrets["GOOGLE_CLIENT_ID"],
    "GOOGLE_CLIENT_SECRET": secrets["GOOGLE_CLIENT_SECRET"],
    "GCS_ROOT_PATH": os.environ["GCS_ROOT_PATH"],
    "DATASTORE_PROJECT": "flask-boilerplate",
    "GCP_CREDENTIALS": credentials,
    "GCP_CREDENTIALS_2": credentials2,
    "SECRET_KEY": secrets["SECRET_KEY"],
}

if os.environ.get("DEV_OVERRIDE_USER"):
    config["DEV_OVERRIDE_USER"] = os.environ["DEV_OVERRIDE_USER"]

app = create_app(config)
