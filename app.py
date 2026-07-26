import os
import streamlit as st
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

from blog_summary import summarize_blog

load_dotenv()

st.set_page_config(
    page_title="Podcast Generator AI",
    page_icon="🎙️",
    layout="centered"
)

st.title("AI Podcast Generator")
st.caption("Turn any article or webpage URL into an audio podcast!")


def text_to_speech_elevenlabs(text: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL") -> bytes:
    """
    Uses ElevenLabs API to convert text script into an MP3 audio byte stream.
    Default voice_id is set to 'Rachel'.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY is missing from environment variables.")

    client = ElevenLabs(api_key=api_key)

    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2"
    )
    
    audio_bytes = b"".join(chunk for chunk in audio_generator if isinstance(chunk, bytes))
    return audio_bytes


url_input = st.text_input(
    "Paste Website or Article Link:",
    placeholder="https://example.com/blog-post"
)

if st.button("Generate Podcast", type="primary", use_container_width=True):
    if not url_input:
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("🕷️ Scraping URL & Generating Podcast Script..."):
            try:
                generated_script = summarize_blog(url_input)
                st.session_state["generated_script"] = generated_script
            except Exception as e:
                st.error(f"Error generating text script: {e}")
                st.stop()

        with st.spinner("🎙️ Generating Voice Audio via ElevenLabs..."):
            try:
                audio_data = text_to_speech_elevenlabs(
                    text=st.session_state["generated_script"]
                )
                st.session_state["audio_bytes"] = audio_data
                st.success("Podcast generation complete!")
            except Exception as e:
                st.error(f"Failed to generate ElevenLabs Audio: {e}")

st.divider()

if "generated_script" in st.session_state:
    st.subheader("Generated Podcast Script")
    st.text_area(
        label="Script Output",
        value=st.session_state["generated_script"],
        height=200,
        disabled=True
    )

if "audio_bytes" in st.session_state:
    st.subheader("Listen to Your Podcast")
    
    st.audio(st.session_state["audio_bytes"], format="audio/mp3", autoplay=True)
    
    st.download_button(
        label="Download Podcast MP3",
        data=st.session_state["audio_bytes"],
        file_name="podcast.mp3",
        mime="audio/mp3"
    )