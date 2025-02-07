from slack_bolt import App
from flask import Flask, request, jsonify
import os
import openai

# Load environment variables (Set these in Render)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Flask app (Handles Slack’s challenge & health check)
flask_app = Flask(__name__)

# Initialize Slack App
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

# 🔹 Health Check Endpoint (Prevents 404 Errors)
@flask_app.route("/", methods=["GET"])
def health_check():
    return "Slack Bot is Running!", 200

# 🔹 Handle Slack's URL verification challenge
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        print("Slack Challenge Received:", data["challenge"])
        return jsonify({"challenge": data["challenge"]})  # ✅ Fix: Correctly return challenge value
    return jsonify({"status": "ok"}), 200  

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

# 🔹 Listen for Slack mentions
@app.event("app_mention")
def handle_mention(event, say):
    print(f"🔹 Received Slack event: {event}")  # Debugging log
    user_message = event.get("text", "")
    print(f"🔹 User Message: {user_message}")  # Debugging log

    ai_response = ask_ai(user_message)  # Call OpenAI function
    print(f"🔹 AI Response: {ai_response}")  # Debugging log

    say(ai_response)  # Send response back to Slack

# Run Flask server (Slack expects this to stay running)
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)
