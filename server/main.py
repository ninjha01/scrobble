import os

import yaml
from google.oauth2 import service_account
from google.cloud import pubsub_v1


try:
    from webapp.app import create_app
except (ModuleNotFoundError, ImportError):
    from .webapp.app import create_app


key_path = "secret.json"
credentials = service_account.Credentials.from_service_account_file(key_path)

with open("./secret.yaml") as f:
    secrets = yaml.load(f, Loader=yaml.SafeLoader)["env_variables"]

config = {
    "SECRET_KEY": secrets["SECRET_KEY"],
    "GCP_CREDENTIALS": credentials,
    "PUBSUB_VERIFICATION_TOKEN": secrets["PUBSUB_VERIFICATION_TOKEN"],
    "PUBSUB_TOPIC": "scrobble",
    "PROJECT": "scrobble",
}

if os.environ.get("DEV_OVERRIDE_USER"):
    config["DEV_OVERRIDE_USER"] = os.environ["DEV_OVERRIDE_USER"]

app = create_app(config)
app.publisher = pubsub_v1.PublisherClient()
