import streamlit as st
from transformers import pipeline

@st.cache_data()
def load_summarizer():
    summarizer = pipeline("summarization")
    return summarizer

def generate_chunks(inp_str):
    max_chunk = 500
    inp_str = inp_str.replace('.', '.<eos>')
    inp_str = inp_str.replace('?', '?<eos>')
    inp_str = inp_str.replace('!', '!<eos>')
    
    sentences = inp_str.split('<eos>')
    current_chunk = 0 
    chunks = []
    for sentence in sentences:
        if len(chunks) == current_chunk + 1: 
            if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            chunks.append(sentence.split(' '))

    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])
    return chunks

def text_summarization_page():
    st.header("Text Summarization")

    article_text = st.text_area("Text to be summarized:", height=200)
    max = st.slider('Select max', 50, 500, step=10, value=350)
    min = st.slider('Select min', 10, 450, step=10, value=100)
    do_sample = st.checkbox("Do sample", value=False)

    if len(article_text) > 100:
        if st.button("Generate Summary"):
            with st.spinner("Generating Summary.."):
                summarizer = load_summarizer()
                chunks = generate_chunks(article_text)
                res = summarizer(chunks,
                                max_length=max, 
                                min_length=min, 
                                do_sample=do_sample)
                text = ' '.join([summ['summary_text'] for summ in res])
                st.info(text)
        
                st.download_button("Download Summary", text, "summary.txt", "text/plain")

    else:
        st.warning("The text you entered is too short")