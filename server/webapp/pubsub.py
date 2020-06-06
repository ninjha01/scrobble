from dataclasses import dataclass
from flask import (
    Blueprint,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
    Response,
    jsonify,
)
import json
import base64
from typing import Iterator, Dict, Any, Optional, List
from .models import (
    does_session_exist,
    does_user_exist,
    does_round_exist,
    get_round,
    get_session,
    get_user,
)


blueprint = Blueprint("pubsub", __name__)


def get_publisher():
    return current_app.publisher


@dataclass
class Message:
    msg_type: str
    data: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


def dict_to_message(d: Dict[Any, Any]) -> Optional[Message]:
    return Message(msg_type=d["msg_type"], data=d["data"])


MESSAGES: List[Message] = []


def publish(message: bytes, topic=None):
    project = current_app.config["PROJECT"]
    topic = topic if topic else current_app.config["PUBSUB_TOPIC"]
    publisher = get_publisher()
    topic_path = publisher.topic_path(project, topic)
    publisher.publish(topic_path, data=message)
    print(f"Published: {str(message)}")


@blueprint.route("/pubsub/push", methods=["POST"])
def push():
    message_txt = request.form["message"]
    message = Message(
        msg_type="Standard", data={"session_id": "hello", "txt": message_txt}
    )
    publish(bytes(message, "utf-8"))
    return Response(200)


@blueprint.route("/pubsub/<session_id>/start_next_round", methods=["POST"])
def start_next_round(session_id: str) -> Response:
    if not does_session_exist(session_id):
        return jsonify(
            {"success": False, "error": f"Session {session_id} does not exist."}
        )
    session = get_session(session_id)
    assert session is not None

    round_id = session.round_ids[session.current_round]
    round = get_round(round_id)
    assert round is not None

    req = request.get_json(force=True)
    user_id = req.get("user_id", None)

    if user_id is None:
        return jsonify({"success": False, "error": "A username must be provided."})
    if not does_user_exist(user_id):
        return jsonify({"success": False, "error": f"user: {user_id} does not exist."})
    else:
        user = get_user(user_id)
    assert user is not None

    data = {"user_id": user.id, "session_id": session.id, "round_id": round.id}
    message = Message(msg_type="SESSION_START", data=data)
    publish(bytes(message.to_json(), "utf-8",))
    return jsonify({"success": True})


@blueprint.route("/pubsub/listen", methods=["POST"])
def listen():
    if request.args.get("token", "") != current_app.config["PUBSUB_VERIFICATION_TOKEN"]:
        return "Invalid request", 400

    envelope = json.loads(request.data.decode("utf-8"))
    print("pubsub.listen", "envelope", envelope)
    try:
        # prod
        print("pubsub.listen", "Am I in prod?")
        payload = base64.b64decode(envelope["message"]["data"])
    except TypeError:
        # dev
        print("pubsub.listen", "Am I in dev?")
        payload = envelope["message"]["data"]
    print("pubsub.listen", "payload type", type(payload))
    try:
        message = dict_to_message(json.loads(payload))
        if message is not None:
            print("pubsub.listen", f"Understood {payload}")
            MESSAGES.append(message)
    except (TypeError, KeyError) as e:
        print("pubsub.listen", f"Didn't understand {payload}", e)
    print("pubsub.listen", f"{payload} acked")
    return Response(status=200)


@blueprint.route("/pubsub/<session_id>/stream")
def stream(session_id: str):
    def event_stream() -> Iterator[str]:
        for message in MESSAGES:
            if message.data["session_id"] == session_id:
                yield f"data: {message.to_json()}\n\n"
            else:
                yield "data: crickets\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


@blueprint.route("/pubsub/view", methods=["GET"])
def view():
    return render_template("pages/pubsub_template.html", messages=MESSAGES)
