from openai_utils import ask_ai  # ✅ Import the updated AI function

@app.event("app_mention")
def handle_mention(event, say):
    user_message = event.get("text", "").lower().replace("@ai assistant bot", "").strip()

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
