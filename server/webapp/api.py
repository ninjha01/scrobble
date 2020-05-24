from collections import defaultdict
import requests
import json
from flask import (
    Flask,
    Blueprint,
    url_for,
    request,
    jsonify,
    current_app,
)
from .models import (
    does_user_exist,
    create_user as _create_user,
    get_user,
    does_session_exist,
    create_session as _create_session,
    get_session,
    add_user_word_to_round,
    get_round,
)


blueprint = Blueprint("api", __name__)

app = Flask(__name__)


@blueprint.route("/solve/<word>", methods=["GET"])
def solve_word(word):
    print("called")
    url = f"https://wordsolver.net/solvewords.php?arg=%23!q%3D{word}%26f%3D%26ftype%3Df_none%26dic%3Dd_twl%26type%3Dst_anagram%26ml%3D15%26ne%3D1%26cb%3D29767902096514387&_=1589737771353"
    response = requests.get(url)
    response_json = json.loads(response.content[19:])
    length_word_map = response_json["m"]

    word_length_dict = defaultdict(lambda: 0)
    for length, words in length_word_map.items():
        for w in words.keys():
            word_length_dict[w.lower()] = int(length)
    return word_length_dict


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

    # user_id = req["user_id"]

    # if not does_user_exist(user_id):
    #     user = _create_user(user_id)
    # else:
    #     user = get_user(user_id)

    num_rounds = int(req["num_rounds"])
    session = _create_session(session_id=session_id, num_rounds=num_rounds)
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

    user_word = req.get("user_word", "")

    print(session_id, user_id, user_word)

    add_user_word_to_round(round.id, user.id, user_word)
    round = get_round(round_id)
    return jsonify({"success": True, "user_words": round.user_words[user.id]})


@blueprint.route("/session/create", methods=["POST"])
def create_round():
    pass
