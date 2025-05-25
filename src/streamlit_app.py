import streamlit as st
import tempfile
import pandas as pd
import asyncio
import os
from time import time

from model.book import Book
from utils.pricing import estimate_total_cost, get_time_until_saver_mode
from utils.translator import Translator
from utils.translation_manager import TranslationManager
from utils.epub_exporter import export_translated_epub

st.title("Epub Translator")

uploaded_file = st.file_uploader("Upload your English EPUB book", type=["epub"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    book = Book(tmp_path, tokenizer_dir="deepseek_v3_tokenizer")
    book_id = uploaded_file.name.replace(".epub", "")
    manager = TranslationManager(book, max_concurrent=5, book_id=book_id)
    total_tokens = book.get_num_tokens()

    # Section: Cost Estimate
    total_cost, tier = estimate_total_cost(total_tokens)

    # Section: Book Stats
    st.subheader("Book Information")
    stats_df = pd.DataFrame({
        "Statistic": ["Chapters", "Paragraphs", "Tokens", "Cost (USD)"],
        "Detail": [
            book.get_num_chapters(),
            book.get_num_paragraphs(),
            total_tokens,
            total_cost
        ]
    }).set_index("Statistic")
    st.dataframe(stats_df)

    if tier == "discount":
        st.markdown('<span style="color: green;">Currently in Saver Mode (50% Discount Active)</span>', unsafe_allow_html=True)
    else:
        delta = get_time_until_saver_mode()
        if delta:
            hours, remainder = divmod(delta.seconds, 3600)
            minutes = remainder // 60
            st.markdown(f"<span style='color: orange;'>Saver mode starts in {hours}h {minutes}min (UTC 16:30)</span>", unsafe_allow_html=True)

    # Preview Translation
    st.subheader("Preview Translation")
    if st.button("Translate a Sample Paragraph"):
        translator = Translator()
        sample_para = None
        for chapter in book.chapters:
            for paragraph in chapter.split("\n"):
                if len(paragraph.split()) > 40:
                    sample_para = paragraph.strip()
                    break
            if sample_para:
                break

        if sample_para:
            st.markdown("**Original Paragraph:**")
            st.write(sample_para)
            with st.spinner("Translating..."):
                translated = translator.translate_to_french(sample_para)
            st.markdown("**Translated Paragraph:**")
            st.write(translated)
        else:
            st.warning("No paragraph longer than 20 words was found.")

    # Translation and Export Controls
    st.subheader("Translate and Export")
    col1, col2, col3 = st.columns(3)

    with col1:
        translate_clicked = st.button("Translate Entire Book")
    with col2:
        stop_clicked = st.button("Stop Translation")
    with col3:
        export_clicked = st.button("Export Translated Book")

    if stop_clicked:
        manager.request_stop()

    if translate_clicked:
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        table_placeholder = st.empty()
        start_time = time()

        def update_progress(translated, total, cost, elapsed, remaining):
            percent = translated / total
            progress_bar.progress(percent)
            elapsed_m, elapsed_s = divmod(int(elapsed), 60)
            remaining_m, remaining_s = divmod(int(remaining), 60)

            progress_data = pd.DataFrame({
                "Metric": ["Progress", "Cost (USD)", "Completed", "Elapsed", "Estimated Time Left"],
                "Value": [
                    f"{translated}/{total} paragraphs",
                    f"${cost:.4f}",
                    f"{percent*100:.2f}%",
                    f"{elapsed_m}m {elapsed_s}s",
                    f"{remaining_m}m {remaining_s}s"
                ]
            }).set_index("Metric")

            table_placeholder.dataframe(progress_data, use_container_width=True)

        translated_output = asyncio.run(manager.translate_all(progress_callback=update_progress))

    if export_clicked:
        if not manager.cache:
            st.warning("No translations available in cache. Please translate some paragraphs first.")
        else:
            with st.spinner("Generating translated EPUB for download..."):
                try:
                    output_path = export_translated_epub(
                        book=book,
                        cache=manager.cache,
                        book_identifier=manager.book_identifier,
                        cache_dir=manager.cache_dir
                    )
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="Download Translated EPUB",
                            data=f,
                            file_name=f"translated_{book_id}.epub",
                            mime="application/epub+zip",
                            key="download_translated_epub"
                        )
                    st.success(f"Translated EPUB ready for download: {output_path}")
                    try:
                        os.unlink(output_path)
                    except Exception:
                        pass  # Ignore cleanup errors
                except Exception as e:
                    st.error(f"Error generating EPUB: {e}")
