import os
import streamlit as st
import requests
import io
import base64
from dotenv import load_dotenv

# load_dotenv()
# api_key = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_KEY=st.secrets["AZURE_SPEECH_KEY"]
AZURE_REGION=st.secrets["AZURE_REGION"]
MODAL_NAME=st.secrets["MODAL_NAME"]

def text_to_speech(text):
    url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_SPEECH_KEY,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
        'User-Agent': 'streamlit'
    }
    
    # Create SSML string
    ssml = f"""<speak version='1.0' xml:lang='en-US'>
        <voice xml:lang='en-US' xml:gender='Female' name='{MODAL_NAME}'>
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
    if not all(k in st.secrets for k in ["AZURE_SPEECH_KEY", "AZURE_REGION", "MODAL_NAME"]):
        st.error("Azure credentials not found in secrets. Please add them to continue.")
        return
    
    st.title("Text to Speech Converter")
    # Text input
    text_input = st.text_area("Enter text to convert to speech", 
                             "Enter your text here...")
    
    # Convert button
    if st.button("Convert to Speech"):
        
        if text_input and text_input != "Enter your text here...":
            with st.spinner("Converting text to speech..."):
                audio_data = text_to_speech(text_input)
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


# import streamlit as st
# import requests
# import time

# DJANGO_API_URL_EXECUTE = "http://127.0.0.1:8000/execute_tts_fetcher/"
# DJANGO_API_URL_STATUS = "http://127.0.0.1:8000/get_tts_fetcher_task_status/"

# def initiate_task(text):
#     """Start the TTS task via Django API"""
#     try:
#         data = {'text': text}
#         resp = requests.post(DJANGO_API_URL_EXECUTE, data=data)
#         resp.raise_for_status()
        
#         rj = resp.json()
#         if rj.get('status') == 'success' and 'task_id' in rj:
#             return rj['task_id']
#         else:
#             st.error(f"Failed to initiate task: {rj}")
#             return None
#     except requests.RequestException as e:
#         st.error(f"Error initiating task: {str(e)}")
#         return None

# def check_task_status(task_id, timeout=300, interval=5):
#     """Poll the TTS task status until completion."""
#     start_time = time.time()
    
#     while time.time() - start_time < timeout:
#         try:
#             resp = requests.get(DJANGO_API_URL_STATUS, params={'task_id': task_id})
#             resp.raise_for_status()
            
#             rj = resp.json()
#             status = rj.get('status')
            
#             if status == 'SUCCESS':
#                 return rj.get('audio_url')  # Return S3 URL
#             elif status == 'PENDING':
#                 print("Task is still pending. Waiting...")
#             else:
#                 st.error(f"Task failed with status: {status}")
#                 return None
            
#             time.sleep(interval)
#         except requests.RequestException as e:
#             st.error(f"Error checking task status: {str(e)}")
#             return None
    
#     st.error("Task timed out.")
#     return None

# def main():
#     st.title("Apper Text-to-Speech Generator")
#     st.write("Enter text and generate a downloadable audio file.")

#     text = st.text_area("Enter Text:")

#     if st.button("Generate Audio"):
#         if text.strip():
#             with st.spinner("Initiating task..."):
#                 task_id = initiate_task(text)
            
#             if not task_id:
#                 st.error("Failed to initiate TTS task.")
#                 return
            
#             with st.spinner("Processing..."):
#                 s3_url = check_task_status(task_id)
            
#             if s3_url:
#                 st.success("Audio generated successfully!")
#                 st.audio(s3_url, format="audio/mp3")
#                 st.markdown(f"[Download MP3]({s3_url})")
#             else:
#                 st.error("Failed to retrieve audio.")
#         else:
#             st.warning("Please enter text.")

# if __name__ == "__main__":
#     main()

# import os
# import streamlit as st
# from azure.cognitiveservices.speech import (
#     SpeechConfig,
#     SpeechSynthesizer,
#     AudioConfig,
#     SpeechSynthesisOutputFormat
# )
# from azure.cognitiveservices.speech import ResultReason, CancellationReason
# import uuid

# import dotenv
# dotenv.load_dotenv()

# # Set up Azure credentials - Replace with your actual values
# AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
# AZURE_REGION = os.getenv("AZURE_REGION")


# def text_to_speech(text, output_file="output.mp3"):
#     # Create speech config
#     speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
#     speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
    
#     # Set output format using the enum
#     speech_config.set_speech_synthesis_output_format(
#         SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
#     )
    
#     # Create audio config
#     audio_config = AudioConfig(filename=output_file)
    
#     # Create synthesizer
#     synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
#     # Synthesize text
#     result = synthesizer.speak_text_async(text).get()
    
#     if result.reason == ResultReason.SynthesizingAudioCompleted:
#         return True
#     elif result.reason == ResultReason.Canceled:
#         cancellation = result.cancellation_details
#         st.error(f"Speech synthesis canceled: {cancellation.reason}")
#         if cancellation.reason == CancellationReason.Error:
#             st.error(f"Error details: {cancellation.error_details}")
#         return False

# def main():
#     st.title("Text to Speech Converter")
#     st.subheader("Using Microsoft Azure Cognitive Services")
    
#     # Text input
#     text = st.text_area("Enter text to convert to speech:", height=200)
    
#     # Generate button
#     if st.button("Generate Audio"):
#         if text.strip() == "":
#             st.warning("Please enter some text!")
#             return
            
#         with st.spinner("Generating audio..."):
#             # Create unique filename
#             filename = f"downloads/audio_{uuid.uuid4().hex}.mp3"
            
#             # Generate audio
#             success = text_to_speech(text, filename)
            
#             if success:
#                 st.success("Audio generated successfully!")
                
#                 # Show audio player and download button
#                 with open(filename, "rb") as f:
#                     audio_bytes = f.read()
                
#                 st.audio(audio_bytes, format="audio/mp3")
                
#                 st.download_button(
#                     label="Download MP3",
#                     data=audio_bytes,
#                     file_name="generated_audio.mp3",
#                     mime="audio/mp3"
#                 )

# if __name__ == "__main__":
#     # Create downloads directory if not exists
#     if not os.path.exists("downloads"):
#         os.makedirs("downloads")
#     main()