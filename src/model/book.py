import os
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup
from transformers import AutoTokenizer

class Book:
    def __init__(self, file_path, tokenizer_dir="deepseek-chat"):
        self.book = epub.read_epub(file_path)
        self.chapters = self._extract_chapters()

        abs_tokenizer_dir = os.path.abspath(tokenizer_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(abs_tokenizer_dir, trust_remote_code=True)

    def _extract_chapters(self):
        chapters = []
        for item in self.book.get_items():
            if item.get_type() == ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text = soup.get_text(separator="\n").strip()
                if text:
                    chapters.append(text)
        return chapters

    def get_num_chapters(self):
        return len(self.chapters)

    def get_num_paragraphs(self):
        return sum(len(chapter.split('\n')) for chapter in self.chapters)

    def get_num_tokens(self):
        total_tokens = 0
        for chapter in self.chapters:
            tokens = self.tokenizer.encode(chapter, add_special_tokens=False)
            total_tokens += len(tokens)
        return total_tokens
