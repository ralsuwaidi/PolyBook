# utils/translator.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class Translator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("DEEP_SEEK_API"), base_url="https://api.deepseek.com")

    def translate_to_french(self, text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that translates English to French while maintaining the original meaning and style."},
                    {"role": "user", "content": f"Translate this into French:\n{text}"}
                ],
                temperature=0.5,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during translation: {e}"
