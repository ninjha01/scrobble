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
)
import json
import base64
from google.cloud import pubsub_v1

blueprint = Blueprint("pubsub", __name__)
MESSAGES = []


@blueprint.route("/pubsub/push", methods=["POST"])
def push():
    if request.args.get("token", "") != current_app.config["PUBSUB_VERIFICATION_TOKEN"]:
        return "Invalid request", 400

    envelope = json.loads(request.data.decode("utf-8"))
    payload = envelope["message"]["data"]
    publish(bytes(payload, "utf-8"))
    # Returning any 2xx status indicates successful receipt of the message.
    return Response(200)


publisher = pubsub_v1.PublisherClient()


def publish(message: str, topic=None):
    project = current_app.config["PROJECT"]
    topic = topic if topic else current_app.config["PUBSUB_TOPIC"]
    topic_path = publisher.topic_path(project, topic)
    publisher.publish(topic_path, data=message)
    print("Published")


@blueprint.route("/pubsub/listen", methods=["POST"])
def listen():
    print("recieved")
    if request.args.get("token", "") != current_app.config["PUBSUB_VERIFICATION_TOKEN"]:
        return "Invalid request", 400
    envelope = json.loads(request.data.decode("utf-8"))
    payload = base64.b64decode(envelope["message"]["data"])
    MESSAGES.append(payload)
    print(f"{payload} acked")
    return Response(200)


@blueprint.route("/pubsub/view", methods=["GET"])
def view():
    return render_template("pages/pubsub_template.html", messages=MESSAGES)


# curl -i -H "Content-Type: application/json" --data @sample_message.json "localhost:5000/pubsub/push?token=f903fd06-2778-4b88-a9f3-f0dc7b29d540"
