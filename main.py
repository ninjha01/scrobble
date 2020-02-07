import os
import yaml

from webapp.app import create_app

config = {
    "SECRET_KEY": os.environ["SECRET_KEY"],
}


if os.environ.get("DEV_OVERRIDE_USER"):
    config["DEV_OVERRIDE_USER"] = os.environ["DEV_OVERRIDE_USER"]

app = create_app(config)
