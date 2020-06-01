import yaml
from google.oauth2 import service_account
import sys
import os

sys.path.insert(0, "~/Desktop/scrobble/")
from server.webapp.app import create_app  # noqa


key_path = "./server/scrobble-3f6552fc61a6.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
assert os.path.exists(key_path)
credentials = service_account.Credentials.from_service_account_file(key_path)

with open("./server/secret.yaml") as f:
    secrets = yaml.load(f, Loader=yaml.SafeLoader)["env_variables"]

config = {"SECRET_KEY": secrets["SECRET_KEY"], "GCP_CREDENTIALS": credentials}


app = create_app(config)
ctx = app.test_request_context()
ctx.push()

try:
    get_user()  # type: ignore
except (NameError, ImportError):
    import server.webapp.models as models
    from server.webapp.models import *  # noqa
except TypeError:
    import importlib

    importlib.reload(models)
    from server.webapp.models import *  # noqa
