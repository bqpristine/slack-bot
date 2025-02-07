from slack_bolt import App
from flask import Flask, request, jsonify
import os
import openai
import requests  # ✅ Added for downloading files from Slack
from slack_bolt.adapter.flask import SlackRequestHandler

# 🔹 Import Google Drive API Dependencies
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload  # ✅ Fixed missing import

# 🔹 Google Drive Credentials Path (stored as a secret file in Render)
GOOGLE_DRIVE_CREDENTIALS_PATH = "/etc/secrets/google_drive_credentials.json"

# 🔹 Google Drive Folder ID (Provided by user)
GOOGLE_DRIVE_FOLDER_ID = "1P8XbcFiDgCfJv3QKlmgfS5GjJ3XMiFZE"

def upload_to_google_drive(file_path, file_name, folder_id=GOOGLE_DRIVE_FOLDER_ID):
    """Uploads a file to a specific folder in Google Drive"""
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
        return f"📂 File uploaded successfully: {file_link}"
    except Exception as e:
        print(f"🚨 Google Drive Upload Error: {e}")
        return f"Error uploading file to Google Drive: {e}"
        
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

@app.event("app_mention")
def handle_mention(event, say):
    user_message = event.get("text", "").lower()

    if "generate file" in user_message or "create document" in user_message:
        # 🔹 AI Generates Content
        document_content = ask_ai("Generate a summary about " + user_message)
        
        # 🔹 Save Content to a File
        file_name = "AI_Generated_Document.txt"
        file_path = f"/tmp/{file_name}"
        with open(file_path, "w") as file:
            file.write(document_content)

        # 🔹 Upload File to Google Drive
        drive_response = upload_to_google_drive(file_path, file_name, GOOGLE_DRIVE_FOLDER_ID)
        
        # 🔹 Reply with Google Drive Link
        say(f"📄 AI-created file uploaded: {drive_response}")
    
    elif "upload file" in user_message:
        files = event.get("files", [])

        if not files:
            say("Please upload a file along with your message.")
            return
        
        file_info = files[0]
        file_url = file_info.get("url_private_download")
        file_name = file_info.get("name")

        # 🔹 Download File from Slack
        local_file_path = f"/tmp/{file_name}"
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        response = requests.get(file_url, headers=headers)

        if response.status_code == 200:
            with open(local_file_path, "wb") as file:
                file.write(response.content)

            # 🔹 Upload to Google Drive
            drive_response = upload_to_google_drive(local_file_path, file_name, GOOGLE_DRIVE_FOLDER_ID)
            say(f"📂 {drive_response}")  
        else:
            say("⚠️ Error downloading file from Slack. Please check file permissions.")
    
    else:
        say("I can help with file management! Say 'upload file' to upload an existing file or 'generate file' to create one.")



# 🔹 Handle direct messages and channel messages
@app.event("message")
def handle_message_events(event, say):
    event_id = event.get("event_ts", "")  # Unique event timestamp from Slack
    if event_id in processed_events:
        print(f"🔹 Ignored duplicate event: {event_id}")  # Debugging log
        return  # Ignore duplicate event
    processed_events.append(event_id)  # Mark event as processed

    print(f"🔹 Processing Message Event: {event}")  # Debugging log
    user_message = event.get("text", "")
    print(f"🔹 User Message: {user_message}")  # Debugging log

    ai_response = ask_ai(user_message)  # Call OpenAI function
    print(f"🔹 AI Response: {ai_response}")  # Debugging log

    say(ai_response)  # Send response back to Slack

# 🔹 Run Flask server (Slack expects this to stay running)
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)  # ✅ Only run Flask, Slack events are handled by Bolt inside Flask
