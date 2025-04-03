import streamlit as st
import os
import json
import sounddevice as sd
import shutil
from scipy.io.wavfile import write
import subprocess
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(page_title="911 Call AI Monitoring Dashboard", layout="centered")
st.title("🚨 911 Call AI Monitoring Dashboard")

# Upload audio
uploaded_file = st.file_uploader("Upload a 911 Call (.wav)", type=["wav"])

if uploaded_file:
    st.success("📂 File uploaded. Now analyzing...")

    # Save uploaded file to correct location
    temp_path = "data/audio_files/temp_audio.wav"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    # Run the pipeline scripts
    os.system("python3 scripts/audio_diarization.py")
    os.system("python3 scripts/categorize_call.py")
    os.system("python3 scripts/evaluate_operator.py")

    # Display the outputs
    try:
        with open("data/categorized_calls/categorized_call.json") as f:
            category_data = json.load(f)
            st.subheader("🗂 Call Category")
            st.json(category_data)
    except:
        st.warning("⚠️ Categorization failed.")

    try:
        with open("data/operator_evaluation/operator_evaluation.json") as f:
            eval_data = json.load(f)
            st.subheader("📋 Operator Evaluation")
            st.json(eval_data)
    except:
        st.warning("⚠️ Operator evaluation failed.")

# Load final report
report_path = "data/final_911_report.json"

if not os.path.exists(report_path) or os.stat(report_path).st_size == 0:
    st.warning("No report data available. Click above to record a test call.")
else:
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
