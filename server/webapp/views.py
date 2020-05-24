from flask import (
    Blueprint,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from .forms import ForgotForm, LoginForm, RegisterForm
from .models import create_session as _create_session
from .models import create_user as _create_user
from .models import (
    does_session_exist,
    does_user_exist,
    get_session,
    get_user,
    get_round,
)

blueprint = Blueprint("views", __name__)


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
    user = get_user(user_id)

    if not does_session_exist(session_id):
        print(f"Invalid session id: {session_id}.")
        flash(f"Invalid session id: {session_id}.")
        return redirect(url_for("views.home"))
    session = get_session(session_id)
    round_num = session.current_round
    round = get_round(session.round_ids[round_num])
    return render_template(
        "pages/session_template.html",
        user_id=user.id,
        session_id=session.id,
        round_num=round_num,
        round_str=round.round_str,
    )
