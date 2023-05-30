import streamlit as st
from pytube import YouTube
import os
import pandas as pd
import requests

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

headers = {
    "authorization": st.secrets["auth_key"],
    "content-type": "application/json"
}

@st.cache_data
def save_audio(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
    base, ext = os.path.splitext(out_file)
    file_name = base + '.mp3'
    os.rename(out_file, file_name)
    print(yt.title + " has been successfully downloaded.")
    print(file_name)
    return yt.title, file_name

@st.cache_data
def upload_to_AssemblyAI(save_location):
    CHUNK_SIZE = 5242880
    print(save_location)

    def read_file(filename):
        with open(filename, 'rb') as _file:
            while True:
                print("chunk uploaded")
                data = _file.read(CHUNK_SIZE)
                if not data:
                    break
                yield data

    upload_response = requests.post(
        upload_endpoint,
        headers=headers, data=read_file(save_location)
    )
    print(upload_response.json())

    audio_url = upload_response.json()['upload_url']
    print('Uploaded to', audio_url)

    return audio_url

@st.cache_data
def start_analysis(audio_url):
    print(audio_url)

    ## Start transcription job of audio file
    data = {
        'audio_url': audio_url,
        'iab_categories': True,
        'content_safety': True,
        "summarization": True,
        "summary_type": "bullets"
    }

    transcript_response = requests.post(transcript_endpoint, json=data, headers=headers)
    print(transcript_response)

    transcript_id = transcript_response.json()['id']
    polling_endpoint = transcript_endpoint + "/" + transcript_id

    print("Transcribing at", polling_endpoint)
    return polling_endpoint
    
@st.cache_data
def get_analysis_results(polling_endpoint):

    status = 'submitted'

    while True:
        print(status)
        polling_response = requests.get(polling_endpoint, headers=headers)
        status = polling_response.json()['status']
        # st.write(polling_response.json())
        # st.write(status)

        if status == 'submitted' or status == 'processing' or status == 'queued':
            print('not ready yet')
            sleep(10)

        elif status == 'completed':
            print('creating transcript')

            return polling_response

            break
        else:
            print('error')
            return False
            break        

def youtube_summarization_page():
    st.header("Youtube Video Summarization")

    st.markdown("Make sure your links are in the format: https://www.youtube.com/watch?v=HfNnuQOHAaw and not https://youtu.be/HfNnuQOHAaw")

    default_bool = st.checkbox("Try it out with a default link")

    video_url = st.text_input('Youtube Video Link')

    if st.button("Generate Summary"):
        if default_bool:
            video_url = "https://www.youtube.com/watch?v=Mmt936kgot0&t=489s"

        if video_url is not None:

            video_title, save_location = save_audio(video_url)

            st.header(video_title)
            st.audio(save_location)
        
            # upload mp3 file to AssemblyAI
            audio_url = upload_to_AssemblyAI(save_location)

            # start analysis of the file
            polling_endpoint = start_analysis(audio_url)

            # receive the results
            results = get_analysis_results(polling_endpoint)

            summary = results.json()['summary']

            st.header("Summary of this video")
            st.info(summary)

            st.download_button("Download Summary", summary, "summary.txt", "text/plain")

