from slack_bolt import App
from openai_utils import ask_ai, download_openai_file
from google_drive_utils import upload_to_google_drive
import os

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

@app.event("app_mention")
def handle_mention(event, say):
    user_message = event.get("text", "").lower()

    if "generate file" in user_message or "create document" in user_message:
        ai_response = ask_ai(f"Generate a detailed report about {user_message}")

        file_name = "AI_Generated_Report.txt"
        file_path = f"/tmp/{file_name}"

        # Save AI-generated text as a file
        with open(file_path, "w") as file:
            file.write(ai_response)

        # Upload file to Google Drive
        drive_link = upload_to_google_drive(file_path, file_name)

        say(f"📂 AI-generated report uploaded! Download it here: {drive_link}")

    elif "upload openai file" in user_message:
        file_id = "file-NeZJuw5QEA9jZiUf6NKhFU"
        file_path, file_name = download_openai_file(file_id)

        if file_path:
            drive_link = upload_to_google_drive(file_path, file_name)
            say(f"📂 OpenAI file uploaded! Download it here: {drive_link}")
        else:
            say("⚠️ Failed to download OpenAI file.")

    else:
        say("I can help with file management! Say 'upload OpenAI file' to upload the latest file.")


@app.event("message")
def handle_message_events(event, say, client, logger):
    try:
        logger.info(f"🔹 Received message event: {event}")
        user_message = event.get("text", "")

        # Ignore messages from the bot itself
        bot_user_id = client.auth_test()["user_id"]
        if event.get("user") == bot_user_id:
            return  

        ai_response = ask_ai(user_message)

        # 🔹 Define the channel explicitly (replace with a valid Slack channel ID)
        channel_id = event.get("channel", "YOUR_DEFAULT_CHANNEL_ID")  # <-- Replace this with your channel ID

        client.chat_postMessage(channel=channel_id, text=ai_response)

    except Exception as e:
        logger.error(f"🚨 Error handling message event: {e}")
        client.chat_postMessage(channel=channel_id, text="⚠️ I encountered an error while processing your message.")
