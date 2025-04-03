import os
import whisper
from pyannote.audio import Pipeline
import torch

# Load Whisper model
model = whisper.load_model("medium")

# Load Pyannote pipeline for diarization (using your READ token)
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=HUGGINGFACE_TOKEN
)

# Define audio file (your recorded file)
audio_file = "data/audio_files/temp_audio.wav"

# Perform Whisper transcription
transcript_result = model.transcribe(audio_file)

# Perform Pyannote diarization
diarization_result = pipeline(audio_file)

# Print diarization results
print("Speaker-differentiated Transcript:\n")

for segment, _, speaker in diarization_result.itertracks(yield_label=True):
    # Extract timestamp
    start_time = round(segment.start, 2)
    end_time = round(segment.end, 2)

    # Extract corresponding Whisper transcript segment
    segment_transcript = ""
    for whisper_segment in transcript_result["segments"]:
        if whisper_segment["start"] >= segment.start and whisper_segment["end"] <= segment.end:
            segment_transcript += whisper_segment["text"].strip() + " "

    print(f"[{speaker}] ({start_time}s - {end_time}s): {segment_transcript.strip()}")
