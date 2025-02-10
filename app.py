import re
from elevenlabs import VoiceSettings
import streamlit as st
from elevenlabs.client import ElevenLabs


# Initialize the ElevenLabs client
client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])

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
                "description": voice.description or ""
            }
            for voice in response.voices
        ]
    except Exception as e:
        st.error(f"Error fetching voices: {str(e)}")
        return []

def text_to_speech(text: str, voice_id: str, speed: float) -> bytes:
    """Convert text to speech using ElevenLabs API"""
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.0, use_speaker_boost=True, speed=speed),
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        # Convert the generator to bytes
        return b''.join(audio)
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

def clean_text(text: str) -> str:
    """
    Clean text by removing or replacing special characters.
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Cleaned text
    """
    # Dictionary of replacements (add more as needed)
    replacements = {
        '&': 'and',
        '+': 'plus',
        '@': 'at',
        '#': 'number',
        '%': 'percent',
        '=': 'equals',
        '<': 'less than',
        '>': 'greater than'
    }
    
    # First replace known special characters with their word equivalents
    for char, replacement in replacements.items():
        text = text.replace(char, f' {replacement} ')
    
    # Remove any remaining special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def main():
    st.title("Apper.io Text-to-Speech Converter")
    st.info("Generate high-quality audio using Apper io AI voices. [Elevenlabs]")

    voices = fetch_voices()
    
    if not voices:
        st.error("Failed to load voices. Check your API key and network connection.")
        return

    # Create voice selection dropdown with additional info
    voice_display = [
        f"{v['name']} ({v['category']})" + (f" - {v['description']}" if v['description'] else "")
        for v in voices
    ]
    
    # Find the index of "Apper-Voice-01" in the voice_display list
    default_voice_name = "Apper-Voice-01"
    default_index = next(
        (index for index, voice in enumerate(voice_display) if default_voice_name in voice),
        0  # Fallback to index 0 if "Apper-Voice-01" is not found
    )
    voice_sel, speed_sel = st.columns([8, 4])
    with voice_sel:
        selected_voice = st.selectbox(
            "Select Voice",
            options=voice_display,
            index=default_index
        )
    
    with speed_sel:
        modal_speed = st.slider("Select Speed", min_value=0.5, max_value=2.0, value=0.75, step=0.05)
    # Get the corresponding voice ID
    selected_voice_id = voices[voice_display.index(selected_voice)]["id"]

    # Text input with character limit
    text_input = st.text_area(
        "Enter text to convert to speech (max 5000 characters)",
        placeholder="Type or paste your text here...",
        height=400,
        max_chars=5000
    )

    if st.button("Generate Audio"):
        if text_input.strip():
            text_input = clean_text(text_input)
            with st.spinner("Generating audio..."):
                audio_data = text_to_speech(text_input, selected_voice_id, modal_speed)
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