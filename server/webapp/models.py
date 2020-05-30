from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, DefaultDict, Set, Optional
from uuid import uuid4
import datetime
from .db import DB
from .utils import gen_round_str, pull_score_dict

db = DB()


@dataclass
class User:
    id: str


class UserDoesNotExist(Exception):
    pass


def does_user_exist(user_id: str) -> bool:
    if user_id is None or len(user_id) == 0:
        return False
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
    score_dict: Dict[str, int]
    end_time: Optional[datetime.datetime]

    @property
    def id(self):
        return f"<session: {self.session_id}, number: {self.number}>"


class RoundDoesNotExist(Exception):
    pass


def does_round_exist(round_id: str) -> bool:
    return not db.get_round(round_id) is None


# https://stackoverflow.com/questions/16439301/cant-pickle-defaultdict
# Can't pickle lambdas
def user_words_func():
    return []


def create_round(
    session_id: str, number: int, word_length=10, round_str=None, end_time=None
) -> Round:
    user_words: DefaultDict[str, List[str]] = defaultdict(user_words_func)
    if round_str is None:
        round_str = gen_round_str(word_length)

    score_dict = pull_score_dict(round_str)
    r = Round(
        session_id=session_id,
        number=number,
        round_str=round_str,
        user_words=user_words,
        score_dict=score_dict,
        end_time=end_time,
    )
    db.store_round(r)
    return r


def add_user_word_to_round(round_id: str, user_id: str, word: str):
    r = get_round(round_id)
    u = get_user(user_id)
    r.user_words[u.id].append(word)
    db.store_round(r)


def get_round(round_id: str):
    if does_round_exist(round_id):
        return db.get_round(round_id)
    else:
        raise RoundDoesNotExist


def score_round(round_id) -> Dict[str, int]:
    r = get_round(round_id)
    scores = defaultdict(lambda: 0)
    for user_id, word_list in r.user_words.items():
        scores[user_id] = max([r.score_dict[w] for w in word_list])
    return dict(scores)


@dataclass
class Session:
    id: str
    users: Set[str]
    round_ids: List[str]
    current_round: str


class SessionDoesNotExist(Exception):
    pass


def does_session_exist(session_id: str) -> bool:
    if session_id is None:
        return False

    return not db.get_session(session_id) is None


def add_user_to_session(user_id: str, session_id: str) -> Session:
    u = get_user(user_id)
    s = get_session(session_id)
    s.users.add(u.id)
    db.store_session(s)
    return s


def create_session(
    session_id: str,
    num_rounds: int,
    current_round=0,
    rounds=None,
    start_time=None,
    starting_user=None,
) -> Session:
    assert not does_session_exist(session_id)
    if rounds is None:
        rounds = [
            create_round(session_id=session_id, number=i) for i in range(num_rounds)
        ]
    else:
        assert num_rounds == len(rounds)
    round_ids = [r.id for r in rounds]
    users = set()
    if starting_user is not None:
        users.add(get_user(starting_user).id)
    s = Session(
        id=session_id, round_ids=round_ids, current_round=current_round, users=users
    )
    db.store_session(s)
    return s


def get_session(session_id: str) -> Session:
    if does_session_exist(session_id):
        return db.get_session(session_id)
    else:
        raise SessionDoesNotExist
