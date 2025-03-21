import os
import subprocess
import json

# Paths to scripts
AUDIO_CAPTURE_SCRIPT = "scripts/audio_capture.py"
DIARIZATION_SCRIPT = "scripts/audio_diarization.py"
CATEGORIZATION_SCRIPT = "scripts/categorize_call.py"
EVALUATION_SCRIPT = "scripts/evaluate_operator.py"

# Output files
AUDIO_FILE = "temp_audio.wav"
DIARIZED_FILE = "data/diarized_transcript.json"
CATEGORY_FILE = "data/call_category.json"
EVALUATION_FILE = "data/operator_evaluation.json"

def run_script(script):
    """Runs a script using subprocess and returns its output."""
    result = subprocess.run(["python3", script], capture_output=True, text=True)
    print(f"🔹 Running {script}...\n{result.stdout}")
    if result.stderr:
        print(f"⚠️ Error in {script}:\n{result.stderr}")
    return result.stdout

print("🚀 Starting 911 Call Processing Pipeline...\n")

# Step 1: Capture Audio
run_script(AUDIO_CAPTURE_SCRIPT)

# Step 2: Perform Speaker Diarization and Transcription
run_script(DIARIZATION_SCRIPT)

# Step 3: Categorize the Call
category_output = run_script(CATEGORIZATION_SCRIPT)

# Step 4: Evaluate Operator Performance
evaluation_output = run_script(EVALUATION_SCRIPT)

# Load Results
try:
    with open(CATEGORY_FILE, "r") as f:
        category_data = json.load(f)
except:
    category_data = {}

try:
    with open(EVALUATION_FILE, "r") as f:
        evaluation_data = json.load(f)
except:
    evaluation_data = {}

# Final Output
final_result = {
    "call_category": category_data,
    "operator_evaluation": evaluation_data
}

# Save final results
FINAL_OUTPUT_FILE = "data/final_911_report.json"
with open(FINAL_OUTPUT_FILE, "w") as f:
    json.dump(final_result, f, indent=4)

print(f"\n✅ Process Completed! Results saved in: {FINAL_OUTPUT_FILE}")
