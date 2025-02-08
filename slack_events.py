from openai_utils import ask_ai
from google_drive_utils import upload_to_google_drive
import os
import requests

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

def handle_mention(event, say):
    """Handles mentions in Slack and processes AI requests."""
    user_message = event.get("text", "").lower()

    if "generate file" in user_message or "create document" in user_message:
        topic = user_message.replace("generate file", "").replace("create document", "").strip()
        if not topic:
            topic = "Artificial Intelligence Overview"

        ai_response = ask_ai(f"Generate a detailed report on {topic}")

        file_name = f"AI_Report_{topic.replace(' ', '_')}.txt"
        file_path = f"/tmp/{file_name}"

        with open(file_path, "w") as file:
            file.write(ai_response)

        drive_link = upload_to_google_drive(file_path, file_name)

        say(f"📂 AI-generated report uploaded! Download it here: {drive_link}")

    else:
        say("I can help with file management! Say 'generate file' or 'upload file'.")

def handle_message_events(event, say):
    """Handles messages in Slack."""
    user_message = event.get("text", "").lower()

    ai_response = ask_ai(user_message)
    say(ai_response)
