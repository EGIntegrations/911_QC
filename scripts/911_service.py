import os
import time
import subprocess

# Paths to scripts
AUDIO_CAPTURE_SCRIPT = "scripts/audio_capture.py"
DIARIZATION_SCRIPT = "scripts/audio_diarization.py"
CATEGORIZATION_SCRIPT = "scripts/categorize_call.py"
EVALUATION_SCRIPT = "scripts/evaluate_operator.py"
LOG_FILE = "logs/service.log"

def run_script(script):
    """Runs a script and logs output."""
    result = subprocess.run(["python3", script], capture_output=True, text=True)
    log_entry = f"🔹 {script} output:\n{result.stdout}\n"
    
    with open(LOG_FILE, "a") as log:
        log.write(log_entry)

    if result.stderr:
        with open(LOG_FILE, "a") as log:
            log.write(f"⚠️ Error in {script}:\n{result.stderr}\n")
    
    return result.stdout

print("🚀 911 Call Processing Service Started...\n")

while True:
    print("\n🔄 Checking for new calls...\n")
    
    # Step 1: Capture and process a new call
    run_script(AUDIO_CAPTURE_SCRIPT)
    run_script(DIARIZATION_SCRIPT)
    run_script(CATEGORIZATION_SCRIPT)
    run_script(EVALUATION_SCRIPT)

    print("✅ Call processed successfully!")
    print("\n⏳ Waiting for the next call... (checking every 30 seconds)")
    
    time.sleep(30)  # Adjust based on call center requirements
