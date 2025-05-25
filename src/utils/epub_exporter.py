from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup
from pathlib import Path

def export_translated_epub(book, cache, book_identifier, cache_dir=".translation_cache"):
    """
    Export an EPUB with translated paragraphs from the cache, preserving original HTML structure.
    
    Args:
        book: Book object containing the original EPUB and chapters.
        cache: Dictionary mapping para_id to translated text.
        book_identifier: Unique identifier for the book (used for output file naming).
        cache_dir: Directory to save the output EPUB.
    
    Returns:
        str: Path to the exported EPUB file.
    """
    # Create a new EPUB book
    translated_book = epub.EpubBook()
    
    # Extract metadata from the original EPUB
    original_book = book.book  # Access the ebooklib.EpubBook object
    title = original_book.get_metadata('DC', 'title')
    title = title[0][0] if title else f"Translated Book {book_identifier[:8]}"
    translated_book.set_identifier(f"{book_identifier}_translated")
    translated_book.set_title(title)
    translated_book.set_language("fr")

    # Add authors if available
    authors = original_book.get_metadata('DC', 'creator')
    for author in authors or []:
        translated_book.add_author(author[0])

    # Process each chapter
    chapters = []
    chapter_index = 0
    for item in original_book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            # Get original HTML content
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            
            # Extract text to match with cache (same logic as Book._extract_chapters)
            original_text = soup.get_text(separator="\n").strip()
            if not original_text:
                continue  # Skip empty documents
            
            # Split original text into paragraphs for para_id matching
            original_paragraphs = original_text.split("\n")
            para_id_to_index = {f"{chapter_index}:{hash(p)}": i for i, p in enumerate(original_paragraphs) if p.strip()}
            
            # Find all text-containing elements (e.g., <p>, <div>, <span>)
            text_elements = soup.find_all(text=True)
            current_para_index = 0
            paragraph_texts = original_paragraphs[:]
            
            for element in text_elements:
                # Skip empty or whitespace-only text nodes
                text = element.strip()
                if not text:
                    continue
                
                # Find the paragraph in original_paragraphs that contains this text
                for i, para in enumerate(paragraph_texts[current_para_index:], start=current_para_index):
                    if text in para:
                        para_id = f"{chapter_index}:{hash(para)}"
                        if para_id in cache:
                            # Replace the exact text content with the translation
                            translated_text = cache[para_id]
                            # Ensure the translated text replaces only the text node, preserving tags
                            if translated_text.strip():
                                element.replace_with(translated_text)
                            else:
                                element.replace_with("")
                        current_para_index = i + 1
                        break
            
            # Create EPUB chapter with modified HTML
            epub_chapter = epub.EpubHtml(
                title=f"Chapter {chapter_index + 1}",
                file_name=f"chap_{chapter_index + 1}.xhtml",
                lang="fr"
            )
            epub_chapter.content = str(soup).encode("utf-8")
            translated_book.add_item(epub_chapter)
            chapters.append(epub_chapter)
            chapter_index += 1

    # Add navigation and spine
    translated_book.toc = chapters
    translated_book.add_item(epub.EpubNcx())
    translated_book.add_item(epub.EpubNav())
    translated_book.spine = ['nav'] + chapters

    # Save the EPUB file
    output_path = Path(cache_dir) / f"translated_{book_identifier}.epub"
    epub.write_epub(str(output_path), translated_book)
    return str(output_path)