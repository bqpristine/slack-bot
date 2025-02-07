from slack_bolt import App
from flask import Flask, request, jsonify
import os
import openai
import requests  # ✅ Added for downloading files from Slack
from slack_bolt.adapter.flask import SlackRequestHandler

# 🔹 Import Google Drive API Dependencies
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔹 Google Drive Credentials Path (stored as a secret file in Render)
GOOGLE_DRIVE_CREDENTIALS_PATH = "/etc/secrets/google_drive_credentials.json"

# 🔹 Google Drive Folder ID (Provided by user)
GOOGLE_DRIVE_FOLDER_ID = "1P8XbcFiDgCfJv3QKlmgfS5GjJ3XMiFZE"

# 🔹 Function to Upload Files to Google Drive
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
        print(f"🔹 File uploaded to folder: {file_link}")
        return f"📂 AI-generated file uploaded! Download it here: {file_link}"
    except Exception as e:
        print(f"🚨 Google Drive Upload Error: {e}")
        return f"Error uploading file to Google Drive: {e}"

# 🔹 Function to Generate AI Content & Upload as a File
def generate_ai_file(ai_function, user_message):
    """Generates text using AI, saves it as a file, and uploads it to Google Drive."""
    try:
        # 🔹 Generate AI Content
        document_content = ai_function(f"Generate a detailed report about {user_message}")

        # 🔹 Save AI Content as a Text File
        file_name = "AI_Generated_Report.txt"
        file_path = f"/tmp/{file_name}"
        
        with open(file_path, "w") as file:
            file.write(document_content)

        # 🔹 Upload File to Google Drive
        return upload_to_google_drive(file_path, file_name)

    except Exception as e:
        print(f"🚨 Error generating AI file: {e}")
        return f"⚠️ Error generating file: {e}"

# 🔹 Function to Upload an Existing Slack File
def upload_existing_file(event, slack_token):
    """Handles Slack file uploads by downloading & uploading to Google Drive."""
    files = event.get("files", [])

    if not files:
        return "⚠️ Please upload a file along with your message."

    file_info = files[0]
    file_url = file_info.get("url_private_download")
    file_name = file_info.get("name")

    local_file_path = f"/tmp/{file_name}"
    headers = {"Authorization": f"Bearer {slack_token}"}
    
    response = requests.get(file_url, headers=headers)
    
    if response.status_code == 200:
        with open(local_file_path, "wb") as file:
            file.write(response.content)

        return upload_to_google_drive(local_file_path, file_name)
    else:
        return "⚠️ Error downloading file from Slack. Please check file permissions."

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
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # New API client format
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_response = response.choices[0].message.content
        print(f"🔹 OpenAI Response: {ai_response}")  # Debugging log
        return ai_response
    except Exception as e:
        print(f"🚨 OpenAI API Error: {str(e)}")  # Log the error
        return f"I'm having trouble connecting to AI services right now. Error: {str(e)}"

from collections import deque

processed_events = deque(maxlen=100)  # Store last 100 processed events

# 🔹 Handle Direct Mentions
@app.event("app_mention")
def handle_mention(event, say):
    user_message = event.get("text", "").lower()

    if "generate file" in user_message or "create document" in user_message:
        response = generate_ai_file(ask_ai, user_message)
    elif "upload file" in user_message:
        response = upload_existing_file(event, SLACK_BOT_TOKEN)
    else:
        response = "I can help with file management! Say 'upload file' to upload an existing file or 'generate file' to create one."

    say(response)

# 🔹 Handle Direct Messages and Channel Messages
@app.event("message")
def handle_message_events(event, say, logger):
    try:
        logger.info(f"🔹 Received message event: {event}")
        user_message = event.get("text", "")

        # Ignore messages from the bot itself to prevent infinite loops
        if event.get("user") == app.client.auth_test()["user_id"]:
            return  

        ai_response = ask_ai(user_message)
        say(ai_response)
    except Exception as e:
        logger.error(f"🚨 Error handling message event: {e}")
        say("⚠️ I encountered an error while processing your message.")

# 🔹 Run Flask server (Slack expects this to stay running)
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)  # ✅ Only run Flask, Slack events are handled by Bolt inside Flask
