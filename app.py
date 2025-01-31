import streamlit as st
import requests
from typing import List, Dict

AZURE_SPEECH_KEY = st.secrets["AZURE_SPEECH_KEY"]
AZURE_REGION = st.secrets["AZURE_REGION"]
DEFAULT_VOICE = "en-US-AvaMultilingualNeural"

@st.cache_data(ttl=3600)  # Cache the voice list for 1 hour
def fetch_voices() -> List[Dict]:
    """Fetch available voices from Azure API"""
    url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list"
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_SPEECH_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            voices = response.json()
            # Filter and sort voices
            english_voices = [
                {
                    'display_name': v['DisplayName'],
                    'short_name': v['ShortName'],
                    'gender': v['Gender'],
                    'locale': v['Locale']
                }
                for v in voices
                if v['Locale'].startswith('en-')  # Filter for English voices
            ]
            return sorted(english_voices, key=lambda x: x['display_name'])
        else:
            st.error(f"Failed to fetch voices: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching voices: {str(e)}")
        return []

def text_to_speech(text: str, voice_name: str) -> bytes:
    """Convert text to speech using selected voice"""
    url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_SPEECH_KEY,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
        'User-Agent': 'streamlit'
    }
    
    ssml = f"""<speak version='1.0' xml:lang='en-US'>
        <voice name='{voice_name}'>
            {text}
        </voice>
    </speak>"""
    
    try:
        response = requests.post(url, headers=headers, data=ssml.encode('utf-8'))
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error making API request: {str(e)}")
        return None

def main():
    # Azure credentials check
    if not all(k in st.secrets for k in ["AZURE_SPEECH_KEY", "AZURE_REGION"]):
        st.error("Azure credentials not found in secrets. Please add them to continue.")
        return
    
    st.title("Text to Speech Converter")
    
    # Fetch available voices
    voices = fetch_voices()
    
    # Create voice selection dropdown
    if voices:
        # Create a dictionary mapping display names to short names
        voice_options = {f"{v['display_name']} ({v['gender']})": v['short_name'] for v in voices}
        
        # Find the default voice in the options
        default_idx = list(voice_options.values()).index(DEFAULT_VOICE) if DEFAULT_VOICE in voice_options.values() else 0
        
        # Create the selectbox with display names
        selected_display_name = st.selectbox(
            "Select Voice",
            options=list(voice_options.keys()),
            index=default_idx
        )
        
        # Get the corresponding short name
        selected_voice = voice_options[selected_display_name]
    else:
        selected_voice = DEFAULT_VOICE
        st.warning("Could not fetch voices. Using default voice.")
    
    # Text input
    text_input = st.text_area(
        "Enter text to convert to speech",
        "Enter your text here..."
    )
    
    # Convert button
    if st.button("Convert to Speech"):
        if text_input and text_input != "Enter your text here...":
            with st.spinner("Converting text to speech..."):
                audio_data = text_to_speech(text_input, selected_voice)
                if audio_data:
                    st.success("Audio generated successfully!")
                    # Display audio player
                    st.audio(audio_data, format='audio/mp3')
                    # Download the audio
                    st.download_button(
                        label="Download MP3",
                        data=audio_data,
                        file_name="generated_audio.mp3",
                        mime="audio/mp3"
                    )
        else:
            st.warning("Please enter some text to convert")

if __name__ == "__main__":
    main()
# import os
# import streamlit as st
# import requests
# import io
# import base64

# # load_dotenv()
# # api_key = os.getenv('AZURE_SPEECH_KEY')
# AZURE_SPEECH_KEY=st.secrets["AZURE_SPEECH_KEY"]
# AZURE_REGION=st.secrets["AZURE_REGION"]
# MODAL_NAME=st.secrets["MODAL_NAME"]

# def text_to_speech(text):
#     url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    
#     headers = {
#         'Ocp-Apim-Subscription-Key': AZURE_SPEECH_KEY,
#         'Content-Type': 'application/ssml+xml',
#         'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
#         'User-Agent': 'streamlit'
#     }
    
#     # Create SSML string
#     ssml = f"""<speak version='1.0' xml:lang='en-US'>
#         <voice xml:lang='en-US' xml:gender='Female' name='{MODAL_NAME}'>
#             {text}
#         </voice>
#     </speak>"""
    
#     try:
#         response = requests.post(url, headers=headers, data=ssml.encode('utf-8'))
#         if response.status_code == 200:
#             return response.content
#         else:
#             st.error(f"Error: {response.status_code} - {response.text}")
#             return None
#     except Exception as e:
#         st.error(f"Error making API request: {str(e)}")
#         return None

# def main():
#      # Azure credentials check
#     if not all(k in st.secrets for k in ["AZURE_SPEECH_KEY", "AZURE_REGION", "MODAL_NAME"]):
#         st.error("Azure credentials not found in secrets. Please add them to continue.")
#         return
    
#     st.title("Text to Speech Converter")
#     # Text input
#     text_input = st.text_area("Enter text to convert to speech", 
#                              "Enter your text here...")
    
#     # Convert button
#     if st.button("Convert to Speech"):
        
#         if text_input and text_input != "Enter your text here...":
#             with st.spinner("Converting text to speech..."):
#                 audio_data = text_to_speech(text_input)
#                 if audio_data:
#                     st.success("Audio generated successfully!")
#                     # Display audio player
#                     st.audio(audio_data, format='audio/mp3')
#                     # Download the audio
#                     st.download_button(
#                         label="Download MP3",
#                         data=audio_data,
#                         file_name="generated_audio.mp3",
#                         mime="audio/mp3"
#                     )
#         else:
#             st.warning("Please enter some text to convert")

# if __name__ == "__main__":
#     main()