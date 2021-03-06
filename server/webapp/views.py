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
    session_can_advance,
    does_session_exist,
    does_user_exist,
    add_user_to_session,
    get_session,
    get_user,
    get_round,
    start_round,
    advance_round,
    round_is_over,
    score_round,
    score_session,
)
from .utils import localize_tz

blueprint = Blueprint("views", __name__)


@blueprint.route("/")
def home():
    return render_template("pages/home_template.html")


@blueprint.route("/about")
def about():
    return render_template("pages/about_template.html")


@blueprint.route("/session/view/<session_id>", methods=["GET", "POST"])
@blueprint.route("/session/view/", methods=["GET", "POST"])
def view_session(session_id=None):
    user_id = request.form.get("user_id", None)
    if user_id is None or len(user_id) == 0:
        flash("Please provide a username.")
        return redirect(url_for("views.home"))
    elif not does_user_exist(user_id):
        user = _create_user(user_id)
    user = get_user(user_id)

    if not does_session_exist(session_id):
        flash(f"Invalid session id: {session_id}.")
        return redirect(url_for("views.home"))
    session = add_user_to_session(user.id, session_id)

    round_num = session.current_round
    assert round_num <= len(session.round_ids) - 1
    current_round = get_round(session.round_ids[round_num])

    if round_is_over(current_round.id):
        if session_can_advance(session.id):
            # Go to next round
            session = advance_round(session.id)
            assert round_num <= len(session.round_ids) - 1
            round_num = session.current_round
            current_round = get_round(session.round_ids[round_num])
        else:
            # All rounds are over
            session_scores = score_session(session.id)
            return render_template(
                "pages/session_finished_template.html",
                user_id=user.id,
                session_id=session.id,
                session_scores=session_scores,
            )
    score_dicts = [(r_id, score_round(r_id)) for r_id in session.get_played_rounds()]
    score_dicts = [
        sd if sd else f"No scores for round {r_id}" for r_id, sd in score_dicts
    ]
    # round_times = get_round_times(session_id)
    return render_template(
        "pages/session_template.html",
        user_id=user.id,
        session_id=session.id,
        users=session.users,
        current_round_number=round_num,
        current_round_id=current_round.id,
        score_dicts=score_dicts,
        total_rounds=len(session.round_ids),
    )


@blueprint.route("/session/view/<session_id>/<round_id>", methods=["GET", "POST"])
def view_round(session_id, round_id):
    user_id = request.form.get("user_id", None)
    if user_id is None:
        flash("Please provide a username.")
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
    if round.end_time is None:
        round = start_round(round.id)
    localized_end_time = localize_tz(round.end_time).isoformat()
    return render_template(
        "pages/round_template.html",
        user_id=user.id,
        session_id=session.id,
        round_num=round_num,
        round_str=round.round_str,
        end_time=localized_end_time,
    )
