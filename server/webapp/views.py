from flask import (
    render_template,
    Blueprint,
    request,
    redirect,
    flash,
    url_for,
    get_flashed_messages,
)
from flask_login import login_required
from .forms import LoginForm, RegisterForm, ForgotForm
from .models import (
    does_user_exist,
    create_user as _create_user,
    get_user,
    does_session_exist,
    create_session as _create_session,
    get_session,
)

blueprint = Blueprint("views", __name__)


################
#### routes ####
################


@blueprint.route("/")
def home():
    return render_template("pages/home_template.html")


@blueprint.route("/about")
def about():
    return render_template("pages/about_template.html")


@blueprint.route("/session/view/<session_id>", methods=["GET", "POST"])
def view_session(session_id):
    user_id = request.form.get("user_id", None)
    if user_id is None:
        print("Please provide a username.")
        return redirect(url_for("views.home"))
    elif not does_user_exist(user_id):
        user = _create_user(user_id)
    else:
        user = get_user(user_id)

    print("session", session_id)
    if not does_session_exist(session_id):
        print(f"Invalid session id: {session_id}.")
        flash(f"Invalid session id: {session_id}.")
        return redirect(url_for("views.home"))
    else:
        session = get_session(session_id)
        return render_template(
            "pages/session_template.html", user_id=user.id, session_id=session.id
        )
