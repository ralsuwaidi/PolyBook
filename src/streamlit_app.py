import streamlit as st
import tempfile
import pandas as pd
from model.book import Book
from utils.pricing import estimate_total_cost, get_time_until_saver_mode

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
