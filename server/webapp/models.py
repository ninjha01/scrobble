from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class User:
    id: str
    session: str


@dataclass
class Round:
    session: str
    number: int
    word: str
    user_words: Dict[str, List[str]]

    @property
    def id(self):
        return f"<session: {self.session}, number: {self.number}>"


@dataclass
class Session:
    id: str
    user_ids: List[str]
    round_ids: List[str]
