import streamlit as st
import yt_dlp
import os
from pathlib import Path

import subprocess

try:
    result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        st.info("✅ FFmpeg is available.")
    else:
        st.warning("⚠️ FFmpeg not working.")
except FileNotFoundError:
    st.error("❌ FFmpeg is not installed.")


st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")
st.title("🎬 YouTube Downloader")

url = st.text_input("Enter a YouTube video URL")

download_format = st.radio("Select format:", ("Video", "Audio"))

def get_video_info(url):
    """Returns metadata of the video including title and thumbnail"""
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail')
            }
    except Exception as e:
        return None

if url:
    info = get_video_info(url)
    if info:
        st.image(info["thumbnail"], caption=info["title"], use_container_width=True)
    else:
        st.warning("Could not fetch video info.")

if st.button("Download"):
    if url:
        with st.spinner("Downloading..."):
            output_filename = ""

            if download_format == "Audio":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': 'downloaded_audio.%(ext)s',
                }
                output_filename = 'downloaded_audio.mp3'

            else:  # Video
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': 'downloaded_video.%(ext)s',
                }
                output_filename = 'downloaded_video.mp4'

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                file_bytes = Path(output_filename).read_bytes()
                mime_type = "audio/mp3" if download_format == "Audio" else "video/mp4"
                st.success("Download complete! Your file will start downloading shortly, Click button below if download not started yet.")

                st.download_button(
                label="Download File",
                data=file_bytes,
                file_name=output_filename,
                mime=mime_type
            )


                os.remove(output_filename)

            except Exception as e:
                st.error(f"Download failed: {e}")
    else:
        st.warning("Please enter a YouTube URL.")
