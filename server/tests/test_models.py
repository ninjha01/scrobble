from ..webapp import models
from ..webapp.db import DB
from ..webapp.models import (
    create_round,
    create_session,
    create_user,
    submit_word_to_round,
    score_round,
)


def test_models(tmpdir, monkeypatch):
    monkeypatch.setattr(models, "db", DB(dir=str(tmpdir)))
    u1 = create_user("u1")
    u2 = create_user("u2")
    u3 = create_user("u3")
    print("user_id", u1.id)
    session_id = "test_session"
    rounds = [
        create_round(session_id, 0, round_str="hello"),
        create_round(session_id, 1, round_str="apple"),
        create_round(session_id, 2, round_str="zero"),
    ]
    s = create_session(session_id=session_id, rounds=rounds, num_rounds=len(rounds))
    for r in rounds:
        submit_word_to_round(u1.id, "hello", r.id)
        submit_word_to_round(u2.id, "app", r.id)
        submit_word_to_round(u3.id, "zero", r.id)

    assert score_round(rounds[0].id) == {u1.id: 5, u2.id: 0, u3.id: 0}
    assert score_round(rounds[1].id) == {u1.id: 0, u2.id: 3, u3.id: 0}
    assert score_round(rounds[2].id) == {u1.id: 0, u2.id: 0, u3.id: 4}
