from slack_bolt import App
from flask import Flask, request, jsonify
import os
import openai
import requests
from slack_bolt.adapter.flask import SlackRequestHandler
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔹 Google Drive Credentials Path
GOOGLE_DRIVE_CREDENTIALS_PATH = "/etc/secrets/google_drive_credentials.json"
GOOGLE_DRIVE_FOLDER_ID = "1P8XbcFiDgCfJv3QKlmgfS5GjJ3XMiFZE"

# 🔹 Load API Keys from Environment Variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Initialize Flask App & Slack Bot
flask_app = Flask(__name__)
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler = SlackRequestHandler(app)

# 🔹 Google Drive Upload Function
def upload_to_google_drive(file_path, file_name, folder_id=GOOGLE_DRIVE_FOLDER_ID):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_DRIVE_CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=credentials)

        file_metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(file_path, mimetype="application/octet-stream")

        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        file_link = f"https://drive.google.com/file/d/{file.get('id')}/view"
        print(f"🔹 File uploaded to Google Drive: {file_link}")
        return f"📂 File uploaded successfully! Download it here: {file_link}"

    except Exception as e:
        print(f"🚨 Google Drive Upload Error: {e}")
        return f"Error uploading file to Google Drive: {e}"

# 🔹 OpenAI File Download & Upload to Google Drive
def upload_openai_file(file_id):
    try:
        openai.api_key = OPENAI_API_KEY

        # 🔹 Get file info from OpenAI
        file_info = openai.files.retrieve(file_id)
        file_name = file_info.get("filename", "openai_file.txt")
        
        # 🔹 Download file from OpenAI
        file_content = openai.files.content(file_id)
        local_file_path = f"/tmp/{file_name}"

        with open(local_file_path, "wb") as f:
            f.write(file_content)

        # 🔹 Upload to Google Drive
        return upload_to_google_drive(local_file_path, file_name)

    except Exception as e:
        print(f"🚨 OpenAI File Handling Error: {e}")
        return f"⚠️ Error handling OpenAI file: {e}"

# 🔹 Slack Event: Handle OpenAI File Upload Request
@app.event("app_mention")
def handle_mention(event, say):
    user_message = event.get("text", "").lower()

    if "upload openai file" in user_message:
        file_id = "file-NeZJuw5QEA9jZiUf6NKhFU"  # 🔹 Replace with actual file ID
        response = upload_openai_file(file_id)
    else:
        response = "I can help with file management! Say 'upload OpenAI file' to upload the latest file."

    say(response)

# 🔹 Flask Routes
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/", methods=["GET"])
def health_check():
    return "Slack Bot is Running!", 200

# 🔹 Start Flask Server
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)
