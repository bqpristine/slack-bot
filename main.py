from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import os
from slack_events import handle_mention, handle_message_events

# Load environment variables (Set these in Render)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize Slack App
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler = SlackRequestHandler(app)

# Route for Slack Events
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Health Check Endpoint
@flask_app.route("/", methods=["GET"])
def health_check():
    return "Slack Bot is Running!", 200

# Register Slack event handlers
app.event("app_mention")(handle_mention)
app.event("message")(handle_message_events)

# Run Flask server
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)
