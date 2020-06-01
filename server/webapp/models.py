from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, DefaultDict, Set, Optional, Union
from uuid import uuid4
import datetime
import pytz
from .extensions import db
from .utils import gen_round_str, pull_score_dict
from google.cloud.datastore.entity import Entity


def get_all_of_entity_type(key_type: str) -> List[str]:
    assert key_type in {User.key_type, Round.key_type, Session.key_type}
    query = db.ds_client.query(kind=key_type)
    results = list(query.fetch())
    entity_names = [entity.key.name for entity in results]
    for e in entity_names:
        assert e is not None
    return entity_names


@dataclass
class User:
    id: str
    key_type = "User"

    def to_entity(self) -> Entity:
        key = db.ds_client.key(self.key_type, self.id)
        entity = Entity(key=key)
        return entity


def entity_to_user(entity: Entity) -> Optional[User]:
    if entity is None:
        return None
    return User(id=entity.key.id_or_name)


class UserDoesNotExist(Exception):
    pass


def get_user(user_id: str) -> Optional[User]:
    user_key = db.ds_client.key(User.key_type, user_id)
    user_entity = db.ds_client.get(user_key)
    return entity_to_user(user_entity)


def put_user(u: User):
    assert u is not None
    user_entity = u.to_entity()
    db.ds_client.put(user_entity)


def does_user_exist(user_id: str) -> bool:
    if user_id is None or len(user_id) == 0:
        return False
    return get_user(user_id) is not None


def create_user(user_id: str) -> User:
    assert not does_user_exist(user_id)
    u = User(id=user_id)
    put_user(u)
    return u


@dataclass
class Round:
    session_id: str
    number: int
    round_str: str
    user_words: Dict[str, List[str]]
    score_dict: Dict[str, int]
    end_time: Optional[datetime.datetime] = None
    key_type = "Round"

    @property
    def id(self):
        return f"<session: {self.session_id}, number: {self.number}>"

    def to_entity(self) -> Entity:
        key = db.ds_client.key(self.key_type, self.id)
        entity = Entity(key=key)
        entity["session_id"] = self.session_id
        entity["number"] = self.number
        entity["round_str"] = self.round_str
        entity["user_words"] = self.user_words
        entity["score_dict"] = self.score_dict
        if self.end_time is not None:
            entity["end_time"] = self.end_time.astimezone().isoformat()
        else:
            entity["end_time"] = None
        return entity


def entity_to_round(entity: Entity) -> Optional[Round]:
    if entity is None:
        return None
    if entity["end_time"] is None:
        end_time = None
    else:
        end_time = datetime.datetime.fromisoformat(entity["end_time"])
    return Round(
        session_id=entity["session_id"],
        number=entity["number"],
        round_str=entity["round_str"],
        user_words=defaultdict(user_words_func, entity["user_words"]),
        score_dict=defaultdict(int, entity["score_dict"],),
        end_time=end_time,
    )


class RoundDoesNotExist(Exception):
    pass


class RoundAlreadyStarted(Exception):
    pass


def get_round(round_id: str) -> Optional[Round]:
    round_key = db.ds_client.key(Round.key_type, round_id)
    round_entity = db.ds_client.get(round_key)
    return entity_to_round(round_entity)


def put_round(r: Round):
    assert r is not None
    round_entity = r.to_entity()
    db.ds_client.put(round_entity)


def does_round_exist(round_id: str) -> bool:
    if round_id is None or len(round_id) == 0:
        return False
    return get_round(round_id) is not None


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
    put_round(r)
    return r


def add_user_word_to_round(round_id: str, user_id: str, word: str):
    r = get_round(round_id)
    assert r is not None
    u = get_user(user_id)
    assert u is not None
    r.user_words[u.id].append(word)
    put_round(r)


def start_round(round_id: str, round_duration=60, force=False) -> Round:
    """
    assumes round_duration is in seconds
    """
    r = get_round(round_id)
    assert r is not None
    if not force and r.end_time is not None:
        raise RoundAlreadyStarted
    r.end_time = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(
        seconds=round_duration
    )
    put_round(r)
    return r


def score_round(round_id) -> Dict[str, Tuple[str, int]]:
    r = get_round(round_id)
    assert r is not None
    scores: DefaultDict[str, Tuple[str, int]] = defaultdict(lambda x: (x, 0))
    for user_id, word_list in r.user_words.items():
        max_word, max_score = "", -1
        for w in word_list:
            w_score = r.score_dict[w.lower()]
            if w_score > max_score:
                max_word = w
                max_score = w_score
        scores[user_id] = (max_word, max_score)
    scores["Best Word"] = ("hello", 1)
    return dict(scores)


@dataclass
class Session:
    id: str
    users: Set[str]
    round_ids: List[str]
    current_round: int
    key_type = "Session"

    def to_entity(self) -> Entity:
        key = db.ds_client.key(self.key_type, self.id)
        entity = Entity(key=key)
        entity["id"] = self.id
        entity["users"] = list(self.users)
        entity["round_ids"] = self.round_ids
        entity["current_round"] = self.current_round
        return entity


def entity_to_session(entity: Entity) -> Optional[Session]:
    if entity is None:
        return None
    return Session(
        id=entity["id"],
        users=set(entity["users"]),
        round_ids=entity["round_ids"],
        current_round=entity["current_round"],
    )


class SessionDoesNotExist(Exception):
    pass


def get_session(session_id: str) -> Optional[Session]:
    session_key = db.ds_client.key(Session.key_type, session_id)
    session_entity = db.ds_client.get(session_key)
    return entity_to_session(session_entity)


def put_session(r: Session):
    assert r is not None
    session_entity = r.to_entity()
    db.ds_client.put(session_entity)


def does_session_exist(session_id: str) -> bool:
    if session_id is None or len(session_id) == 0:
        return False
    return get_session(session_id) is not None


def add_user_to_session(user_id: str, session_id: str) -> Session:
    u = get_user(user_id)
    assert u is not None
    s = get_session(session_id)
    assert s is not None
    s.users.add(u.id)
    put_session(s)
    return s


def create_session(
    session_id: str,
    num_rounds: int,
    current_round=0,
    rounds=None,
    start_time=None,
    starting_user_id=None,
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
    if starting_user_id is not None:
        starting_user = get_user(starting_user_id)
        assert starting_user is not None
        users.add(starting_user.id)
    s = Session(
        id=session_id, round_ids=round_ids, current_round=current_round, users=users
    )
    put_session(s)
    return s


def is_session_finished(session_id: str) -> bool:
    s = get_session(session_id)
    assert s is not None
    assert s.current_round <= len(s.round_ids)
    return s.current_round == len(s.round_ids)


def advance_round(session_id: str) -> Session:
    s = get_session(session_id)
    assert s is not None
    assert not is_session_finished(s.id)
    s.current_round += 1
    put_session(s)
    return s


def session_can_advance(session_id) -> bool:
    s = get_session(session_id)
    assert s is not None
    if s.current_round + 1 >= len(s.round_ids):
        return False
    current_round = get_round(s.round_ids[s.current_round])
    assert current_round is not None
    now = datetime.datetime.now(tz=pytz.utc)
    return (
        current_round.end_time is not None
        and not is_session_finished(s.id)
        and now > current_round.end_time
    )


################################################################################
# Danger
################################################################################
def nuke_user(u_id: str):
    u = get_user(u_id)
    assert u is not None
    print(f"Deleting {u.id}")
    db.ds_client.delete(u.to_entity().key)


def nuke_round(r_id: str):
    r = get_round(r_id)
    assert r is not None
    print(f"Deleting {r.id}")
    db.ds_client.delete(r.to_entity().key)


def nuke_session(s_id: str):
    s = get_session(s_id)
    assert s is not None
    for r_id in s.round_ids:
        nuke_round(r_id)
    print(f"Deleting {s.id}")
    db.ds_client.delete(s.to_entity().key)


def nuke_all_sessions():
    assert input("Are you sure you want to nuke all sessions? [yes/no]: ") == "yes"
    [nuke_session(s.id) for s in get_all_of_entity_type(key_type=Session.key_type)]
