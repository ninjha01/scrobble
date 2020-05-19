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
