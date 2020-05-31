import os
import yaml
from google.oauth2 import service_account

try:
    from webapp.app import create_app
except (ModuleNotFoundError, ImportError):
    from .webapp.app import create_app


key_path = "scrobble-3f6552fc61a6.json"
credentials = service_account.Credentials.from_service_account_file(key_path)

with open("./secret.yaml") as f:
    secrets = yaml.load(f, Loader=yaml.SafeLoader)["env_variables"]

config = {"SECRET_KEY": secrets["SECRET_KEY"], "GCP_CREDENTIALS": credentials}

if os.environ.get("DEV_OVERRIDE_USER"):
    config["DEV_OVERRIDE_USER"] = os.environ["DEV_OVERRIDE_USER"]

app = create_app(config)
