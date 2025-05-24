import streamlit as st
import tempfile
import pandas as pd
from model.book import Book
from utils.pricing import estimate_total_cost, get_time_until_saver_mode
from utils.translator import Translator
from utils.translation_manager import TranslationManager

st.title("Epub Translator")

uploaded_file = st.file_uploader("Upload your English EPUB book", type=["epub"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    book = Book(tmp_path, tokenizer_dir="deepseek_v3_tokenizer")
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


if uploaded_file:
    # Preview Translation
    st.subheader("Preview Translation")

    if st.button("Translate a Sample Paragraph"):
        translator = Translator()

        # Find first paragraph > 20 words
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


if uploaded_file:
    manager = TranslationManager(book)

    translate_clicked = st.button("Translate Entire Book")
    stop_clicked = st.button("Stop Translation")

    if stop_clicked:
        manager.request_stop()

    if translate_clicked:
        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        def update_progress(translated, total, cost, elapsed, remaining):
            percent = translated / total
            progress_bar.progress(percent)

            elapsed_m, elapsed_s = divmod(int(elapsed), 60)
            remaining_m, remaining_s = divmod(int(remaining), 60)

            status_placeholder.markdown(f"""
                **Progress:** {translated}/{total} paragraphs  
                **Cost so far:** ${cost:.4f}  
                **Completed:** {percent*100:.2f}%  
                **Elapsed:** {elapsed_m}m {elapsed_s}s  
                **Estimated time left:** {remaining_m}m {remaining_s}s
            """)

        translated_output = manager.translate_all(progress_callback=update_progress)
