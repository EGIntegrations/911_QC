import os
import whisper
from pyannote.audio import Pipeline
import torch
import json

print("Starting audio_diarization.py")

try:
    print("Checking if ffmpeg is installed...")
    if os.system("ffmpeg -version") != 0:
        raise EnvironmentError("ffmpeg is not installed or not found in PATH. Please install ffmpeg and try again.")
    print("Loading Whisper model...")
    # Load Whisper model
    model = whisper.load_model("tiny", device="cpu")

    print("Loading Pyannote diarization pipeline...")
    # Load Pyannote pipeline for diarization (using your READ token)
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=HUGGINGFACE_TOKEN
    )

    # Define audio file (your recorded file)
    audio_file = "data/audio_files/temp_audio.wav"

    print("Transcribing audio with Whisper...")
    # Perform Whisper transcription
    transcript_result = model.transcribe(audio_file)

    print("Running speaker diarization...")
    # Perform Pyannote diarization
    diarization_result = pipeline(audio_file)

    print("Building diarized transcript output...")
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

    # Save full transcript for later use
    diarized_transcript = ""
    for segment, _, speaker in diarization_result.itertracks(yield_label=True):
        start_time = round(segment.start, 2)
        end_time = round(segment.end, 2)
        segment_transcript = ""
        for whisper_segment in transcript_result["segments"]:
            if whisper_segment["start"] >= segment.start and whisper_segment["end"] <= segment.end:
                segment_transcript += whisper_segment["text"].strip() + " "
        diarized_transcript += f"[{speaker}] ({start_time}s - {end_time}s): {segment_transcript.strip()}\n"

    print("Saving transcript to JSON...")
    # Save to JSON
    with open("data/transcripts/diarized_transcript.json", "w") as f:
        json.dump({"transcript": diarized_transcript}, f, indent=2)

    print("audio_diarization.py completed successfully.")
except Exception as e:
    print(f"audio_diarization.py crashed: {e}")
