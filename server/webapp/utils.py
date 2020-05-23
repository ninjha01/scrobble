from random import randint


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
