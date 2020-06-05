import json
from collections import defaultdict

import requests
from flask import Blueprint, Flask, current_app, jsonify, request, url_for, Response
from .models import add_user_word_to_round
from .models import create_session as _create_session
from .models import create_user as _create_user
from .models import (
    does_session_exist,
    does_user_exist,
    does_round_exist,
    get_round,
    get_session,
    get_user,
)
from .utils import pull_score_dict

blueprint = Blueprint("api", __name__)

app = Flask(__name__)


@blueprint.route("/solve/<word>", methods=["GET"])
def solve_word(word):
    return pull_score_dict(word)


@blueprint.route("/user/create", methods=["POST"])
def create_user():
    pass


@blueprint.route("/session/create", methods=["POST"])
def create_session():
    req = request.get_json(force=True)
    session_id = req.get("session_id", "")

    if len(session_id) == 0:
        return jsonify({"success": False, "error": "A session id must be provided."})

    if does_session_exist(session_id):
        return jsonify({"success": False, "error": "Session already exists."})

    user_id = req.get("user_id", None)
    if user_id is None:
        return jsonify({"success": False, "error": "A username must be provided."})
    if not does_user_exist(user_id):
        user = _create_user(user_id)
    else:
        user = get_user(user_id)

    num_rounds = int(req["num_rounds"])
    session = _create_session(
        session_id=session_id, num_rounds=num_rounds, starting_user_id=user.id
    )
    return jsonify(
        {
            "success": True,
            "session_url": url_for("views.view_session", session_id=session.id),
        }
    )


@blueprint.route("/session/submit", methods=["POST"])
def submit_to_session():
    req = request.get_json(force=True)

    session_id = req.get("session_id", None)
    if session_id is None:
        return jsonify({"success": False, "error": "A session id must be provided."})
    elif not does_session_exist(session_id):
        return jsonify(
            {"success": False, "error": f"Session {session_id} doesn't exist."}
        )
    else:
        session = get_session(session_id)

    user_id = req.get("user_id", None)
    if user_id is None:
        return jsonify({"success": False, "error": "A user id must be provided."})
    elif not does_user_exist(user_id):
        return jsonify(
            {"success": False, "error": f"Session {session_id} doesn't exist."}
        )
    else:
        user = get_user(user_id)

    round_id = req.get("round_id", None)
    if round_id is None:
        round_id = session.round_ids[session.current_round]
    elif not does_round_exist(round_id):
        return jsonify({"success": False, "error": f"Round {round_id} doesn't exist."})
    round = get_round(round_id)
    assert round is not None

    user_word = req.get(
        "user_word", ""
    )  # TODO: maybe should return error if no word submitted

    add_user_word_to_round(round.id, user.id, user_word)
    return jsonify({"success": True, "user_words": round.user_words[user.id]})
