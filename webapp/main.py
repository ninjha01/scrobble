import os
import yaml

from .app import create_app

try:
    import googleclouddebugger

    googleclouddebugger.enable()
except ImportError:
    pass

config = {
    "SECRET_KEY": os.environ["SECRET_KEY"],
}

if os.environ.get("DEV_OVERRIDE_USER"):
    config["DEV_OVERRIDE_USER"] = os.environ["DEV_OVERRIDE_USER"]

app = create_app(config)
