import streamlit as st
import json
import os

st.set_page_config(page_title="911 Call AI Dashboard", layout="centered")
st.title("🚨 911 Call AI Monitoring Dashboard")

# Load report
report_path = "data/final_911_report.json"

if not os.path.exists(report_path) or os.stat(report_path).st_size == 0:
    st.warning("No report data available. Please run process_911_call.py first.")
else:
    try:
        with open(report_path, "r") as f:
            report = json.load(f)

        st.subheader("📌 Call Category")
        st.json(report.get("call_category", {}))

        st.subheader("📝 Operator Evaluation")
        st.json(report.get("operator_evaluation", {}))
    except json.JSONDecodeError:
        st.error("The report file exists but is not valid JSON.")

    st.subheader("📌 Call Category")
    st.json(report.get("call_category", {}))

    st.subheader("📝 Operator Evaluation")
    st.json(report.get("operator_evaluation", {}))
