import json

import requests
from flask import (
    Blueprint,
    current_app,
    redirect,
    request,
    url_for,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    get_flashed_messages,
)

from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_manager,
    login_required,
    login_user,
    logout_user,
)

from .forms import LoginForm, RegisterForm, ForgotForm
from .models import User, create_user

blueprint = Blueprint("auth", __name__)


login_manager = LoginManager()


class UnauthorizedUserError(Exception):
    pass


def init_app(app):
    login_manager.init_app(app)
    app.register_blueprint(blueprint)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login"), code=302)


def get_user_id() -> str:
    if current_user.is_anonymous:
        unauthorized()
    else:
        return current_user.id


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@blueprint.route("/login")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(user)
        flash("Logged in successfully.")
        next = request.args.get("next")
        if not is_safe_url(next):
            return flask.abort(400)

        return redirect(next or url_for("index"))
    return render_template("forms/login.html", form=form)


@blueprint.route("/register")
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        login_user(user)
        flash("Logged in successfully.")
        next = request.args.get("next")
        if not is_safe_url(next):
            return flask.abort(400)

        return redirect(next or url_for("index"))
    return render_template("forms/register.html", form=form)


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
