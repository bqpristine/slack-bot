import openai
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ask_ai(prompt):
    """Generates AI text responses while ensuring the AI stays on topic."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # OpenAI API client
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that generates reports and helps with file management."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_response = response.choices[0].message.content
        print(f"🔹 OpenAI Response: {ai_response}")  # Debugging log
        return ai_response
    except Exception as e:
        print(f"🚨 OpenAI API Error: {str(e)}")  # Log the error
        return f"⚠️ AI Error: {str(e)}"


def download_openai_file(file_id):
    """Download a file from OpenAI."""
    try:
        openai.api_key = OPENAI_API_KEY
        file_info = openai.files.retrieve(file_id)
        file_name = file_info.get("filename", "openai_file.txt")
        
        file_content = openai.files.content(file_id)
        local_file_path = f"/tmp/{file_name}"

        with open(local_file_path, "wb") as f:
            f.write(file_content)

        return local_file_path, file_name
    except Exception as e:
        print(f"🚨 OpenAI File Error: {e}")
        return None, f"⚠️ Error: {e}"
