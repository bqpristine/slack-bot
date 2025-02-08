from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# Google Drive Credentials Path
GOOGLE_DRIVE_CREDENTIALS_PATH = "/etc/secrets/google_drive_credentials.json"
GOOGLE_DRIVE_FOLDER_ID = "1P8XbcFiDgCfJv3QKlmgfS5GjJ3XMiFZE"

def upload_to_google_drive(file_path, file_name):
    """Uploads a file to Google Drive and returns the link."""
    if not os.path.exists(file_path):
        return "⚠️ Error: File not found."

    try:
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_DRIVE_CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=credentials)

        file_metadata = {"name": file_name, "parents": [GOOGLE_DRIVE_FOLDER_ID]}
        media = MediaFileUpload(file_path, mimetype="application/octet-stream")

        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        return f"https://drive.google.com/file/d/{file.get('id')}/view"
    except Exception as e:
        return f"⚠️ Google Drive Upload Error: {str(e)}"
