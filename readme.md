
# PolyBook

PolyBook is a Streamlit-based web application that translates English EPUB books into French using the DeepSeek API. It supports asynchronous translation with concurrent API calls, caches translations for efficiency, and allows exporting the translated book as a downloadable EPUB file directly from the browser, preserving the original HTML structure and formatting.

## Features

- **Upload and Parse EPUB**: Upload an English EPUB file and extract its chapters for translation.
- **Asynchronous Translation**: Translate paragraphs concurrently using `aiohttp` and the DeepSeek API, with configurable concurrency limits.
- **Translation Caching**: Store translations in a cache to avoid redundant API calls, using a stable book identifier based on the file name or content hash.
- **Preview Translation**: Preview a sample paragraph translation before processing the entire book.
- **Cost Estimation**: Estimate translation costs based on token counts, with support for a discounted "Saver Mode."
- **Export Translated EPUB**: Export the translated book as a downloadable EPUB, replacing translated paragraphs within their original HTML tags while preserving untranslated content and all formatting.
- **Stop Translation**: Interrupt ongoing translations if needed.
- **User-Friendly Interface**: Built with Streamlit for easy interaction via a web browser.

## Project Structure

```
PolyBook/
├── model/
│   └── book.py             # Book class for EPUB parsing and tokenization
├── utils/
│   ├── epub_exporter.py    # Utility for exporting translated EPUBs
│   ├── pricing.py         # Pricing and cost estimation functions
│   ├── translation_manager.py # Manages translation process and cache
│   └── translator.py      # Handles API calls to DeepSeek for translation
├── streamlit_app.py       # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .translation_cache/    # Directory for cache files and exported EPUBs
└── README.md              # This file
```

## Prerequisites

- **Python**: 3.8 or higher
- **DeepSeek API Key**: Obtain an API key from [DeepSeek](https://www.deepseek.com/) and set it as an environment variable (`DEEP_SEEK_API`).
- **EPUB Files**: Prepare English EPUB files for translation.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/PolyBook.git
   cd PolyBook
   ```

2. **Create a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Create a `requirements.txt` file with the following content:
   ```
   streamlit==1.31.0
   ebooklib==0.18
   beautifulsoup4==4.12.2
   transformers==4.38.1
   aiohttp==3.9.3
   python-dotenv==1.0.1
   pandas==2.2.0
   ```
   Then install:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
   ```
   DEEP_SEEK_API=your_deepseek_api_key_here
   ```
   Alternatively, set the environment variable manually:
   ```bash
   export DEEP_SEEK_API=your_deepseek_api_key_here  # On Windows: set DEEP_SEEK_API=...
   ```

5. **Download Tokenizer** (if not already cached):
   Ensure the `deepseek_v3_tokenizer` directory is available or downloadable by the `transformers` library. If using a specific DeepSeek tokenizer, follow their documentation to set it up.

## Usage

1. **Run the Streamlit App**:
   ```bash
   streamlit run streamlit_app.py
   ```
   This starts a web server, typically at `http://localhost:8501`.

2. **Upload an EPUB**:
   - Open the app in your browser.
   - Use the file uploader to select an English EPUB file.

3. **View Book Stats**:
   - The app displays the number of chapters, paragraphs, tokens, and estimated translation cost.
   - Check if "Saver Mode" (50% discount) is active or when it will start.

4. **Preview Translation**:
   - Click "Translate a Sample Paragraph" to see a sample translation of a paragraph longer than 40 words.

5. **Translate the Book**:
   - Click "Translate Entire Book" to start translating all paragraphs asynchronously.
   - Monitor progress, cost, and estimated time remaining.
   - Click "Stop Translation" to interrupt if needed.

6. **Export Translated EPUB**:
   - Click "Export Translated Book" to generate and download the translated EPUB.
   - The exported EPUB replaces translated paragraphs within their original HTML tags, preserving all formatting (e.g., `<p class="style">Text</p>`), and keeps untranslated paragraphs unchanged.
   - The file downloads as `translated_<filename>.epub` directly in the browser.

7. **Cache Management**:
   - Translations are cached in `.translation_cache/<book_identifier>.json` to avoid redundant API calls.
   - The cache uses the uploaded file’s name as the identifier for consistency across sessions.



## Troubleshooting

- **Download Fails**:
  - Ensure your browser allows downloads from `localhost:8501` (check for pop-up blockers).
  - Check Streamlit logs or the interface for errors.
- **Formatting Issues**:
  - If HTML tags are not preserved, verify that cache entries match the original paragraphs.
  - Add debug prints in `epub_exporter.py`:
    ```python
    print(soup.prettify())  # Before replacement
    print(str(soup))  # After replacement
    ```
- **Cache Issues**:
  - If a new cache is created unexpectedly, ensure the EPUB file is identical across uploads.
  - Clear the cache by deleting `.translation_cache/<book_identifier>.json`.
- **API Errors**:
  - Verify your DeepSeek API key is valid and not rate-limited.
  - Check the `.env` file or environment variable setup.

## Contributing

Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Commit changes (`git commit -m "Add my feature"`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [DeepSeek](https://www.deepseek.com/) for the translation API.
- [Streamlit](https://streamlit.io/) for the web interface framework.
- [ebooklib](https://github.com/aerkalov/ebooklib) for EPUB parsing and creation.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML manipulation.

For issues or feature requests, please open an issue on GitHub.

### Instructions for Use

1. **Copy the Code**:
   - Copy the entire code block above.
   - Paste it into a file named `README.md` in your project’s root directory (`PolyBook/README.md`).

2. **Add to GitHub**:
   - If starting a new repository:
     ```bash
     git init
     git add README.md
     git commit -m "Add PolyBook README"
     git branch -M main
     git remote add origin https://github.com/<your-username>/PolyBook.git
     git push -u origin main
     ```
   - If updating an existing repository:
     ```bash
     git add README.md
     git commit -m "Update README for PolyBook"
     git push origin main
     ```

3. **Add Project Files**:
   - Ensure all project files (`streamlit_app.py`, `model/book.py`, `utils/translation_manager.py`, `utils/epub_exporter.py`, `utils/translator.py`, `utils/pricing.py`) are added:
     ```bash
     git add .
     git commit -m "Add PolyBook project files"
     git push origin main
     ```
   - Create a `.gitignore` file:
     ```
     .translation_cache/
     .env
     venv/
     __pycache__/
     *.pyc
     ```

4. **Create `requirements.txt`**:
   - Save the dependencies in `PolyBook/requirements.txt`:
     ```
     streamlit==1.31.0
     ebooklib==0.18
     beautifulsoup4==4.12.2
     transformers==4.38.1
     aiohttp==3.9.3
     python-dotenv==1.0.1
     pandas==2.2.0
     ```

5. **Verify on GitHub**:
   - Visit `https://github.com/<your-username>/PolyBook`.
   - Confirm the README renders correctly with sections, code blocks, and links.

### Additional Notes

- **GitHub Username**:
  - Replace `<your-username>` with your actual GitHub username. If you provide it, I can update the README with the exact URL.

- **License**:
  - The README assumes an MIT License. Create a `LICENSE` file with the MIT License text if needed:
    ```
    MIT License

    Copyright (c) 2025 <Your Name>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    ```

- **Testing**:
  - Test the setup instructions on a fresh machine to ensure clarity.
  - Verify the browser download functionality (`Export Translated Book` button) produces an EPUB with translated paragraphs in their original HTML tags.

If you need further customizations (e.g., adding a project logo, screenshots, or specific tokenizer setup steps), please let me know!