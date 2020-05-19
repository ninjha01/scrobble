from flask import render_template, Blueprint, request
from .forms import LoginForm, RegisterForm, ForgotForm

blueprint = Blueprint("pages", __name__)


################
#### routes ####
################


@blueprint.route("/")
def home():
    return render_template("pages/home_template.html")


@blueprint.route("/about")
def about():
    return render_template("pages/about_template.html")
