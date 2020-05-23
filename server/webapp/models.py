from uuid import uuid4
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Dict
from .db import DB
from .utils import gen_round_str

db = DB()


@dataclass
class User:
    id: str


class UserDoesNotExist(Exception):
    pass


def does_user_exist(user_id: str) -> bool:
    return not db.get_user(user_id) is None


def create_user(user_id: str) -> User:
    assert not does_user_exist(user_id)
    u = User(id=user_id)
    db.store_user(u)
    return u


def get_user(user_id: str) -> User:
    if does_user_exist(user_id):
        return db.get_user(user_id)
    else:
        raise UserDoesNotExist


@dataclass
class Round:
    session_id: str
    number: int
    round_str: str
    user_words: Dict[str, List[str]]

    @property
    def id(self):
        return f"<session: {self.session_id}, number: {self.number}>"


class RoundDoesNotExist(Exception):
    pass


def does_round_exist(round_id: str) -> bool:
    return not db.get_round(round_id) is None


# https://stackoverflow.com/questions/16439301/cant-pickle-defaultdict
# Can't pickle lambdas
def f():
    return []


def create_round(session_id: str, number: int, word_length=10) -> Round:

    user_words = defaultdict(f)
    r = Round(
        session_id=session_id,
        number=number,
        round_str=gen_round_str(word_length),
        user_words=user_words,
    )
    db.store_round(r)
    return r


def add_user_word_to_round(round_id: str, user_id: str, word: str):
    r = get_round(round_id)
    u = get_user(user_id)
    r.user_words[u.id].append(word)


def get_round(round_id: str):
    if does_round_exist(round_id):
        return db.get_round(round_id)
    else:
        raise RoundDoesNotExist


@dataclass
class Session:
    id: str
    round_ids: List[str]
    current_round: str


class SessionDoesNotExist(Exception):
    pass


def does_session_exist(session_id: str) -> bool:
    return not db.get_session(session_id) is None


def create_session(session_id: str, num_rounds: int, current_round=0) -> Session:
    assert not does_session_exist(session_id)
    rounds = [create_round(session_id=session_id, number=i) for i in range(num_rounds)]
    round_ids = [r.id for r in rounds]
    s = Session(id=session_id, round_ids=round_ids, current_round=current_round)
    db.store_session(s)
    return s


def get_session(session_id: str) -> Session:
    if does_session_exist(session_id):
        return db.get_session(session_id)
    else:
        raise SessionDoesNotExist
