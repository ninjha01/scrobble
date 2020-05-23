import os
import shelve
from typing import Dict, List, Optional, Set, Tuple


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

    def get_session(self, session_id: str):
        with shelve.open(self.session_data_filename) as d:
            return d.get(session_id, None)

    def store_session(self, session):
        with shelve.open(self.session_data_filename) as d:
            d[session.id] = session

    def get_user(self, user_id: str):
        with shelve.open(self.user_data_filename) as d:
            return d.get(user_id, None)

    def store_user(self, user):
        with shelve.open(self.user_data_filename) as d:
            d[user.id] = user

    def get_round(self, round_id: str):
        with shelve.open(self.round_data_filename) as d:
            return d.get(round, None)

    def store_round(self, round):
        with shelve.open(self.round_data_filename) as d:
            d[round.id] = round
