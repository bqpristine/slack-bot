import openai
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ask_ai(prompt):
    """Generate a response using OpenAI's GPT model."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"🚨 OpenAI API Error: {e}")
        return f"⚠️ Error: {e}"

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
