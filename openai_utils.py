import openai
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ask_ai(prompt):
    """Generates AI responses while ensuring meaningful output."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that generates reports and provides informative answers."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"
