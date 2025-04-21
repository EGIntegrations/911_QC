import os
# Extend PATH to include local ffmpeg binary if it exists
ffmpeg_path = os.path.join("bin", "ffmpeg")
if os.path.isfile(ffmpeg_path):
    os.environ["PATH"] = f"{os.path.abspath('bin')}:" + os.environ["PATH"]
    print(f"Using bundled ffmpeg from: {ffmpeg_path}")
from pyannote.audio import Pipeline
import torch
import json

print("Starting audio_diarization.py")

try:
    print("Checking if ffmpeg is installed...")
    if os.system("ffmpeg -version") != 0:
        raise EnvironmentError("ffmpeg is not installed or not found in PATH. Using bundled version failed.")
    print("Transcribing audio with OpenAI Whisper API...")
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Define audio file (your recorded file)
    audio_file = "data/audio_files/temp_audio.wav"

    with open(audio_file, "rb") as audio_file_obj:
        transcript_result = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file_obj
        )
    transcript_text = transcript_result["text"]

    print("Loading Pyannote diarization pipeline...")
    # Load Pyannote pipeline for diarization (using your READ token)
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=HUGGINGFACE_TOKEN
    )


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

        # For now, use the full transcript_text for each segment
        segment_transcript = transcript_text.strip()

        print(f"[{speaker}] ({start_time}s - {end_time}s): {segment_transcript}")

    # Save full transcript for later use
    diarized_transcript = ""
    for segment, _, speaker in diarization_result.itertracks(yield_label=True):
        start_time = round(segment.start, 2)
        end_time = round(segment.end, 2)
        # For now, use the full transcript_text for each segment
        segment_transcript = transcript_text.strip()
        diarized_transcript += f"[{speaker}] ({start_time}s - {end_time}s): {segment_transcript}\n"

    print("Saving transcript to JSON...")
    # Make sure the directory exists
    os.makedirs("data/transcripts", exist_ok=True)
    os.makedirs(os.path.dirname("data/transcripts/diarized_transcript.json"), exist_ok=True)
    # Save to JSON
    with open("data/transcripts/diarized_transcript.json", "w") as f:
        json.dump({"transcript": diarized_transcript}, f, indent=2)

    print("audio_diarization.py completed successfully.")
except Exception as e:
    print(f"audio_diarization.py crashed: {e}")
