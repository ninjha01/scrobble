import os
import shelve
from typing import Dict, List, Optional, Set, Tuple
from models import User, Round, Session


class DB:
    def __init__(self, filename_suffix="db.shelve", dir="."):
        self.filename_suffix = filename_suffix
        self.dir = dir

    @property
    def session_data_filename(self):
        return os.path.join(self.dir, "session-" + self.filename_suffix)

    @property
    def user_data_filename(self):
        return os.path.join(self.dir, "user-" + self.filename_suffix)

    @property
    def round_data_filename(self):
        return os.path.join(self.dir, "round-" + self.filename_suffix)

    def get_session(self, session_id: str) -> Session:
        with shelve.open(self.session_data_filename) as d:
            return d.get(session_id)

    def store_session(self, session: Session):
        with shelve.open(self.session_data_filename) as d:
            d[session.id] = session

    def get_user(self, user_id: str) -> User:
        with shelve.open(self.user_data_filename) as d:
            return d.get(user_id)

    def get_round(self, round_id: str) -> Round:
        with shelve.open(self.round_data_filename) as d:
            return d.get(round_id)

    def store_round(self, round: Round):
        with shelve.open(self.round_data_filename) as d:
            d[round.id] = round
