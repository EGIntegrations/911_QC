import streamlit as st
import os
import json
import sounddevice as sd
from scipy.io.wavfile import write
import subprocess

st.set_page_config(page_title="911 Call AI Dashboard", layout="centered")
st.title("🚨 911 Call AI Monitoring Dashboard")

# Record audio when button is pressed
if st.button("🎙️ Start Test Call (10 sec)"):
    st.info("Recording for 10 seconds. Start talking...")
    fs = 44100
    seconds = 10
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    write("temp_audio.wav", fs, recording)
    st.success("✅ Recorded. Now analyzing...")

    # Run the pipeline
    subprocess.run(["python3", "scripts/audio_diarization.py"])
    subprocess.run(["python3", "scripts/categorize_call.py"])
    subprocess.run(["python3", "scripts/evaluate_operator.py"])

# Load final report
report_path = "data/final_911_report.json"

if not os.path.exists(report_path) or os.stat(report_path).st_size == 0:
    st.warning("No report data available. Click above to record a test call.")
else:
  # after the try block where you loaded the report
try:
    with open(report_path, "r") as f:
        report = json.load(f)

    st.subheader("🗣️ Transcript")
    st.code(report.get("transcript", "Transcript not found."), language="text")

    st.subheader("📌 Call Category")
    st.json(report.get("call_category", {}))

    st.subheader("📝 Operator Evaluation")
    st.json(report.get("operator_evaluation", {}))

except json.JSONDecodeError:
    st.error("The report file exists but is not valid JSON.")
