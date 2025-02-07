import os
import streamlit as st
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Load environment variables
load_dotenv()

# Initialize the ElevenLabs client
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Set up Streamlit app
st.set_page_config(layout="wide", page_icon="https://apper.io/images/fav/apple-icon-180x180.png", page_title="Apper Audio Generation Modal")


@st.cache_data(ttl=3600)
def fetch_voices():
    """Fetch and format available voices from ElevenLabs API"""
    try:
        response = client.voices.get_all()
        return [
            {
                "name": voice.name,
                "id": voice.voice_id,
                "category": voice.category,
                "description": voice.description or "No description"
            }
            for voice in response.voices
        ]
    except Exception as e:
        st.error(f"Error fetching voices: {str(e)}")
        return []

def text_to_speech(text: str, voice_id: str) -> bytes:
    """Convert text to speech using ElevenLabs API"""
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        # Convert the generator to bytes
        return b''.join(audio)
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None


def main():
    st.title("ElevenLabs Text-to-Speech Converter")
    st.info("Generate high-quality audio using ElevenLabs AI voices.")

    voices = fetch_voices()
    
    if not voices:
        st.error("Failed to load voices. Check your API key and network connection.")
        return

    # Create voice selection dropdown with additional info
    voice_display = [
        f"{v['name']} ({v['category']}) - {v['description']}"
        for v in voices
    ]
    
    selected_voice = st.selectbox(
        "Select Voice",
        options=voice_display,
        index=0
    )
    
    # Get the corresponding voice ID
    selected_voice_id = voices[voice_display.index(selected_voice)]["id"]

    # Text input with character limit
    text_input = st.text_area(
        "Enter text to convert to speech (max 5000 characters)",
        placeholder="Type or paste your text here...",
        height=200,
        max_chars=5000
    )

    if st.button("Generate Audio"):
        if text_input.strip():
            with st.spinner("Generating audio..."):
                audio_data = text_to_speech(text_input, selected_voice_id)
                if audio_data:
                    st.success("Audio generated successfully!")
                    st.audio(audio_data, format="audio/mp3")
                    st.download_button(
                        label="Download MP3",
                        data=audio_data,
                        file_name="elevenlabs_audio.mp3",
                        mime="audio/mp3",
                    )
        else:
            st.warning("Please enter some text to convert.")

if __name__ == "__main__":
    main()
# import os
# from dotenv import load_dotenv
# from elevenlabs.client import ElevenLabs
# from elevenlabs import play, save

# load_dotenv()

# # Load the API key from the .env file
# api_key = os.getenv("ELEVENLABS_API_KEY")

# # Initialize the ElevenLabs client with the API key
# client = ElevenLabs(api_key=api_key)

# audio = client.text_to_speech.convert(
#     text="In a quiet village where the sky brushes the fields in hues of gold, young Mia discovered a map leading to forgotten treasures. Little did she know, her cat Whiskers had a secret: he was the guardian of the map, tasked with guiding Mia to not only the treasure but also to her destiny.",
#     voice_id="KWlsl9PZDXTXVygIiX8y",
#     model_id="eleven_multilingual_v2",
#     output_format="mp3_44100_128",
# )

# save(audio, "custom.mp3")