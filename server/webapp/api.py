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

    if "session_id" not in req:
        return jsonify({"success": False, "error": "A session id must be provided."})
    session_id = req["session_id"]

    if does_session_exist(session_id):
        return jsonify({"success": False, "error": "Session already exists."})

    # user_id = req["user_id"]

    # if not does_user_exist(user_id):
    #     user = _create_user(user_id)
    # else:
    #     user = get_user(user_id)

    num_rounds = req["num_rounds"]
    session = _create_session(session_id=session_id, num_rounds=num_rounds)
    return jsonify(
        {
            "success": True,
            "session_url": url_for("views.view_session", session_id=session.id),
        }
    )


@blueprint.route("/session/create", methods=["POST"])
def create_round():
    pass
