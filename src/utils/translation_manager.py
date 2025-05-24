# utils/translation_manager.py
import os
import time
import json
from pathlib import Path
from utils.translator import Translator
from utils.pricing import estimate_total_cost

class TranslationManager:
    def __init__(self, book, cache_dir=".translation_cache"):
        self.book = book
        self.translator = Translator()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        book_identifier = hash("".join(book.chapters))
        self.cache_file = self.cache_dir / f"{book_identifier}.json"
        self.cache = self._load_cache()
        self.stop_requested = False

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

    def translate_all(self, progress_callback=None):
        translated = {}
        total_paragraphs = sum(
            1 for chapter_index, chapter in enumerate(self.book.chapters)
            for paragraph in chapter.split("\n")
            if f"{chapter_index}:{hash(paragraph)}" not in self.cache and paragraph.strip()
        )

        translated_count = 0
        start_time = time.time()

        for chapter_index, chapter in enumerate(self.book.chapters):
            if self.stop_requested:
                break
            translated[chapter_index] = []
            for paragraph in chapter.split("\n"):
                if self.stop_requested:
                    break
                para_id = f"{chapter_index}:{hash(paragraph)}"
                if para_id in self.cache:
                    translated_text = self.cache[para_id]
                    translated[chapter_index].append(translated_text)
                    continue
                elif paragraph.strip():
                    translated_text = self.translator.translate_to_french(paragraph)
                    self.cache[para_id] = translated_text
                    self.save_cache()
                else:
                    translated_text = ""

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