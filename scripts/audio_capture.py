import pyaudio
import wave
import openai
import os
import tempfile

# Set up OpenAI Whisper API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 10  # Adjust length for testing
AUDIO_OUTPUT_FILENAME = "temp_audio.wav"

audio = pyaudio.PyAudio()

# Start Recording
print("🎙 Recording audio... Speak now.")
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

# Stop Recording
audio.terminate()

# Save Audio File
import wave
wf = wave.open(AUDIO_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# Transcribe audio using OpenAI Whisper API (v1+)
print("Transcribing with OpenAI whisper-1...")
with open(AUDIO_OUTPUT_FILENAME, "rb") as audio_file:
    response = openai.Audio.transcriptions.create(
        file=audio_file,
        model="whisper-1"
    )
print("\nTranscription:")
print(response.get("text"))
