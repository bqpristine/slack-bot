from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_events import app

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/", methods=["GET"])
def health_check():
    return "Slack Bot is Running!", 200

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)  # ✅ Ensures Slack events are processed properly
