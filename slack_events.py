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
        ai_text = ask_ai(user_message)
        file_name = "AI_Generated_Report.txt"
        file_path = f"/tmp/{file_name}"

        with open(file_path, "w") as file:
            file.write(ai_text)

        drive_link = upload_to_google_drive(file_path, file_name)
        response = f"📂 AI-generated report uploaded! Download it here: {drive_link}"
    
    elif "upload openai file" in user_message:
        file_id = "file-NeZJuw5QEA9jZiUf6NKhFU"
        file_path, file_name = download_openai_file(file_id)

        if file_path:
            drive_link = upload_to_google_drive(file_path, file_name)
            response = f"📂 OpenAI file uploaded! Download it here: {drive_link}"
        else:
            response = "⚠️ Failed to download OpenAI file."

    else:
        response = "I can help with file management! Say 'upload OpenAI file' to upload the latest file."

    say(response)
