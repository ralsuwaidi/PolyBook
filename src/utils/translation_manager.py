import os
import time
import json
import asyncio
import aiohttp
from pathlib import Path
from utils.translator import Translator
from utils.pricing import estimate_total_cost
import hashlib

class TranslationManager:
    def __init__(self, book, cache_dir=".translation_cache", max_concurrent=5, book_id=None):
        self.book = book
        self.translator = Translator()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        # Use a provided book_id or compute a stable hash of the book content
        if book_id:
            self.book_identifier = book_id
        else:
            self.book_identifier = hashlib.sha256("".join(book.chapters).encode('utf-8')).hexdigest()
        self.cache_file = self.cache_dir / f"{self.book_identifier}.json"
        self.cache = self._load_cache()
        self.stop_requested = False
        self.max_concurrent = max_concurrent

    def _load_cache(self):
        if self.cache_file.exists():
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def reset_cache(self):
        if self.cache_file.exists():
            self.cache_file.unlink()
        self.cache = {}

    def save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def request_stop(self):
        self.stop_requested = True

    async def _translate_paragraph(self, session, para_id, paragraph):
        """Helper method to translate a single paragraph asynchronously."""
        if para_id in self.cache:
            return para_id, self.cache[para_id]
        if not paragraph.strip():
            return para_id, ""
        
        translated_text = await self.translator.translate_to_french_async(session, paragraph)
        self.cache[para_id] = translated_text
        self.save_cache()
        return para_id, translated_text

    async def translate_all(self, progress_callback=None):
        translated = {}
        tasks = []
        total_paragraphs = 0
        paragraphs_to_translate = []

        # Count total paragraphs and prepare tasks
        for chapter_index, chapter in enumerate(self.book.chapters):
            translated[chapter_index] = []
            for paragraph in chapter.split("\n"):
                para_id = f"{chapter_index}:{hash(paragraph)}"
                if para_id not in self.cache and paragraph.strip():
                    total_paragraphs += 1
                    paragraphs_to_translate.append((chapter_index, para_id, paragraph))
                else:
                    translated[chapter_index].append(self.cache.get(para_id, ""))

        translated_count = 0
        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            # Process paragraphs in batches to respect max_concurrent
            for i in range(0, len(paragraphs_to_translate), self.max_concurrent):
                if self.stop_requested:
                    break

                batch = paragraphs_to_translate[i:i + self.max_concurrent]
                tasks = [
                    self._translate_paragraph(session, para_id, paragraph)
                    for chapter_index, para_id, paragraph in batch
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for (chapter_index, para_id, _), (returned_para_id, translated_text) in zip(batch, results):
                    if isinstance(translated_text, Exception):
                        translated_text = f"Error during translation: {translated_text}"
                    translated[chapter_index].append(translated_text)
                    translated_count += 1

                    elapsed = time.time() - start_time
                    percent_complete = translated_count / total_paragraphs if total_paragraphs > 0 else 1
                    est_total_time = elapsed / percent_complete if percent_complete > 0 else 0
                    est_remaining = est_total_time - elapsed

                    cost_so_far, _ = estimate_total_cost(
                        sum(len(p.split()) for p in self.cache.values())
                    )

                    if progress_callback:
                        progress_callback(
                            translated_count,
                            total_paragraphs,
                            cost_so_far,
                            elapsed,
                            est_remaining
                        )

        return translated