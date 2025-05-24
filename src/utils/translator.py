import os
import aiohttp
from dotenv import load_dotenv
import asyncio 
load_dotenv()

class Translator:
    def __init__(self):
        self.api_key = os.getenv("DEEP_SEEK_API")
        self.base_url = "https://api.deepseek.com"

    async def translate_to_french_async(self, session, text: str) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a professional translator specializing in literary texts. "
                                    "Translate English to French accurately, preserving the original meaning, tone, and style of the text. "
                                    "Do not add notes, explanations, or commentary. "
                                    "Translate proper names, titles, and identifiers (e.g., ISBNs) only if necessary to adapt to French conventions, "
                                    "otherwise leave them unchanged. "
                                    "Ensure the translation feels natural and idiomatic in French while staying true to the spirit of the original text."
                                )
                            },
                            {"role": "user", "content": f"Translate this into French:\n{text}"}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1024
                    }
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    error_text = await response.text()
                    return f"Error during translation: HTTP {response.status} - {error_text}"
        except Exception as e:
            return f"Error during translation: {e}"

    def translate_to_french(self, text: str) -> str:
        """Synchronous wrapper for compatibility with existing code."""
        async def sync_wrapper():
            async with aiohttp.ClientSession() as session:
                return await self.translate_to_french_async(session, text)
        return asyncio.run(sync_wrapper())