import json
from collections import defaultdict
from random import randint
from typing import Dict, DefaultDict

import requests


def gen_round_str(word_length: int) -> str:
    popular = "aoeghilruwy"
    others = "bcdfjkmnpqstvxz"
    word = ""
    for j in range(word_length):
        if j < word_length / 2 + 1:
            word += popular[randint(0, len(popular)) - 1]
        else:
            word += others[randint(0, len(others)) - 1]
    return word


# https://stackoverflow.com/questions/16439301/cant-pickle-defaultdict
# Can't pickle lambdas
def word_length_func() -> int:
    return 0


def pull_score_dict(round_str) -> Dict[str, int]:
    url = f"https://wordsolver.net/solvewords.php?arg=%23!q%3D{round_str}%26f%3D%26ftype%3Df_none%26dic%3Dd_twl%26type%3Dst_anagram%26ml%3D15%26ne%3D1%26cb%3D29767902096514387&_=1589737771353"  # noqa
    response = requests.get(url)
    response_json = json.loads(response.content[19:])
    length_word_map = response_json["m"]

    word_length_dict: DefaultDict[str, int] = defaultdict(word_length_func)
    for length, words in length_word_map.items():
        for w in words.keys():
            word_length_dict[w.lower()] = int(length)
    return word_length_dict
