from flask import Flask
from .views import blueprint as views
from flask_humanize import Humanize
import uuid


def create_app(config={}):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(config)
    SECRET_KEY = str(uuid.uuid4())
    app.config["SECRET_KEY"] = SECRET_KEY
    app.register_blueprint(views)
    Humanize(app)
    return app
