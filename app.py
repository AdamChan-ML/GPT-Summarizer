import streamlit as st

from text_summarizer import text_summarization_page
# from youtube_summarizer import 

st.sidebar.title("Summarization Web App")
st.sidebar.markdown("Select the source of summarization accordingly.")
page = st.sidebar.selectbox("Text / Youtube", ("Text", "Youtube"))

if page == "Text":
    text_summarization_page()
else:
    pass