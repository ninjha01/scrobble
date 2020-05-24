from flask import Flask
from flask_login import LoginManager
from .views import blueprint as views
from .api import blueprint as api_blueprint
from .auth import init_app as auth_init_app
from flask_humanize import Humanize
import logging


def create_app(config={}):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "super secret key"
    app.config.update(config)
    app.register_blueprint(views)
    app.register_blueprint(api_blueprint)
    Humanize(app)
    # auth_init_app(app)
    app.logger.setLevel(logging.INFO)
    return app
