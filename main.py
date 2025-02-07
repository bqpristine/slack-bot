from slack_bolt import App
from flask import Flask, request, jsonify
import os
import openai
from slack_bolt.adapter.flask import SlackRequestHandler

# Load environment variables (Set these in Render)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Flask app (Handles Slack’s challenge & health check)
flask_app = Flask(__name__)

# Initialize Slack App
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler = SlackRequestHandler(app)  # Initialize Slack Adapter

# 🔹 Handle Slack Events (Including URL Verification Challenge)
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)  # ✅ Ensures Slack events are processed properly

# 🔹 Health Check Endpoint (Prevents 404 Errors)
@flask_app.route("/", methods=["GET"])
def health_check():
    return "Slack Bot is Running!", 200

# 🔹 AI Function to generate responses
def ask_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        print(f"🔹 OpenAI Response: {response['choices'][0]['message']['content']}")  # Debugging log
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"🚨 OpenAI API Error: {e}")  # Log the error
        return "I'm having trouble connecting to AI services right now."

# 🔹 Handle mentions (@AI Assistant Bot in a channel)
@app.event("app_mention")
def handle_mention(event, say):
    print(f"🔹 Received Slack mention event: {event}")  # Debugging log
    user_message = event.get("text", "")
    print(f"🔹 User Message: {user_message}")  # Debugging log

    ai_response = ask_ai(user_message)  # Call OpenAI function
    print(f"🔹 AI Response: {ai_response}")  # Debugging log

    say(ai_response)  # Send response back to Slack

# 🔹 Handle direct messages and channel messages
@app.event("message")
def handle_message_events(event, say):
    print(f"🔹 Received Message Event: {event}")  # Debugging log
    user_message = event.get("text", "")
    print(f"🔹 User Message: {user_message}")  # Debugging log

    ai_response = ask_ai(user_message)  # Call OpenAI function
    print(f"🔹 AI Response: {ai_response}")  # Debugging log

    say(ai_response)  # Send response back to Slack

# 🔹 Run Flask server (Slack expects this to stay running)
if __name__ == "__main__":
    flask_app.run(ho
