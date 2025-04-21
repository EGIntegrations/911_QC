import streamlit as st
st.set_page_config(page_title="911 Call AI Monitoring Dashboard", layout="centered")

import sys
import os
import json
# Only attempt mic recording when not on Streamlit Cloud
import os as _os_import
try:
    if _os_import.getenv("STREAMLIT_CLOUD") != "true":
        import sounddevice as sd
        from scipy.io.wavfile import write
    else:
        sd = None
        write = None
        st.warning("🎤 Mic recording is only supported locally.")
except ImportError:
    sd = None
    write = None
    st.warning("🎤 Mic recording libraries unavailable.")
import subprocess
from dotenv import load_dotenv
load_dotenv()


st.title("🚨 911 Call AI Monitoring Dashboard")

# Upload audio
uploaded_file = st.file_uploader("Upload a 911 Call (.wav)", type=["wav"])

if uploaded_file:
    st.success("📂 File uploaded. Now analyzing...")

    # Save uploaded file to correct location
    temp_path = "data/audio_files/temp_audio.wav"
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    # Run the pipeline scripts
    st.info("🔊 Running audio_diarization.py...")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/audio_diarization.py"],
            check=True,
            capture_output=True,
            text=True
        )
        st.info("✅ Diarization completed")
        st.code(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("❌ Diarization failed.")
        st.code(e.stderr)
    except Exception as ex:
        st.error(f"⚠️ An unexpected error occurred in audio_diarization.py: {ex}")

    try:
        st.info("📂 Running categorize_call.py...")
        result = subprocess.run(
            [sys.executable, "scripts/categorize_call.py"],
            check=True,
            capture_output=True,
            text=True
        )
        st.info("✅ Categorization completed")
        st.code(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("❌ Categorization failed.")
        st.code(e.stderr)

    try:
        st.info("🧑‍💻 Running evaluate_operator.py...")
        result = subprocess.run(
            [sys.executable, "scripts/evaluate_operator.py"],
            check=True,
            capture_output=True,
            text=True
        )
        st.info("✅ Operator evaluation completed")
        st.code(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("❌ Operator evaluation failed.")
        st.code(e.stderr)

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
