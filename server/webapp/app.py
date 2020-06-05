import logging

from flask import Flask
from flask_humanize import Humanize
from flask_login import LoginManager

from .api import blueprint as api_blueprint
from .views import blueprint as views_blueprint
from .pubsub import blueprint as pubsub_blueprint


def create_app(config={}):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(config)
    app.register_blueprint(views_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(pubsub_blueprint)
    Humanize(app)
    # auth_init_app(app)
    app.logger.setLevel(logging.INFO)
    return app
