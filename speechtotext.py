import os
import subprocess
import getpass
import azure.cognitiveservices.speech as speechsdk
from google.colab import files
from dotenv import load_dotenv

# --------------------------------------------------
# 1. CREATE .env FILE SECURELY
# --------------------------------------------------

speech_key_input = getpass.getpass("Enter your NEW Azure Speech Key: ")

if not speech_key_input.strip():
    raise ValueError("Azure Speech Key is missing.")

endpoint_url = "end
_point"

with open("/content/.env", "w") as env_file:
    env_file.write("AZURE_SPEECH_KEY=" + speech_key_input.strip() + "\n")
    env_file.write("AZURE_SPEECH_ENDPOINT=" + endpoint_url + "\n")

# Load .env
load_dotenv("/content/.env", override=True)

speech_key = os.environ.get("AZURE_SPEECH_KEY")
endpoint_url = os.environ.get("AZURE_SPEECH_ENDPOINT")

# --------------------------------------------------
# 2. UPLOAD MP3 FILE
# --------------------------------------------------

uploaded = files.upload()

if not uploaded:
    raise ValueError("Please upload an MP3 file.")

audio_filename = next(iter(uploaded.keys()))

print("Uploaded:", audio_filename)

# --------------------------------------------------
# 3. CONVERT MP3 TO WAV
# --------------------------------------------------

wav_filename = "/content/converted_audio.wav"

subprocess.run(
    [
        "ffmpeg", "-y", "-i", audio_filename,
        "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le", wav_filename
    ],
    check=True,
    capture_output=True
)

print("Audio converted successfully!")

# --------------------------------------------------
# 4. CONFIGURE AZURE SPEECH
# --------------------------------------------------

speech_config = speechsdk.SpeechConfig(
    subscription=speech_key,
    endpoint=endpoint_url
)

speech_config.speech_recognition_language = "en-US"

audio_config = speechsdk.audio.AudioConfig(
    filename=wav_filename
)

speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config,
    audio_config=audio_config
)

# --------------------------------------------------
# 5. RECOGNIZE SPEECH
# --------------------------------------------------

print("\nStarting speech recognition...")

result = speech_recognizer.recognize_once_async().get()

# --------------------------------------------------
# 6. DISPLAY RESULT
# --------------------------------------------------

if result.reason == speechsdk.ResultReason.RecognizedSpeech:

    print("\n========== RECOGNIZED TEXT ==========")
    print(result.text)
    print("=====================================")

elif result.reason == speechsdk.ResultReason.NoMatch:

    print("No speech could be recognized.")

elif result.reason == speechsdk.ResultReason.Canceled:

    details = result.cancellation_details

    print("Recognition failed!")
    print("Reason:", details.reason)
    print("Error:", details.error_details)
