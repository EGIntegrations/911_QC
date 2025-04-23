import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import re
from typing import Any
load_dotenv()

# Define absolute paths for data directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

station_id = os.getenv("STATION_ID", "UnassignedStation")
STATION_DATA_DIR = os.path.join(DATA_DIR, station_id)
TRANSCRIPT_PATH = os.path.join(STATION_DATA_DIR, "transcripts", "diarized_transcript.json")
CATEGORIZED_DIR = os.path.join(STATION_DATA_DIR, "categorized_calls")
# Ensure directories exist
os.makedirs(os.path.join(STATION_DATA_DIR, "transcripts"), exist_ok=True)
os.makedirs(CATEGORIZED_DIR, exist_ok=True)

# Retrieve your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set.")

# Initialize OpenAI client for the new 1.x SDK
client = OpenAI(api_key=openai_api_key)

# Load actual transcript
with open(TRANSCRIPT_PATH, "r") as f:
    transcript_data = json.load(f)
 # Support both "transcript" and "text" fields
raw = transcript_data.get("transcript") or transcript_data.get("text", "")

# If it's a list of segments, join their 'text' fields
if isinstance(raw, list):
    transcript_text = " ".join(seg.get("text", "") for seg in raw)

# If it's one big string with speaker labels, strip them out
elif isinstance(raw, str):
    transcript_text = re.sub(r"\[.*?\]\s*\(\d+\.\d+s?\s*-\s*\d+\.\d+s?\):\s*", "", raw)

else:
    transcript_text = ""

# Check for high‑priority keywords
keywords_found: list[str] = [
    kw for kw in KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", transcript_text, re.IGNORECASE)
]

print("DEBUG: First 200 characters of transcript_text:", transcript_text[:200])

# Define categories
categories = ["Fire", "Medical", "Domestic Abuse", "Homicide", "Kidnapping", "Robbery", "Other"]

# Keywords that should trigger high‑priority escalation
KEYWORDS = ["gun", "weapon", "knife", "firearm", "shoot", "shooting",
            "explosive", "bomb", "hostage", "kidnap", "abduct"]

# Construct the messages for GPT-4o-mini
messages = [
    {
        "role": "system",
        "content": "You are an expert in classifying 911 call transcripts. Respond ONLY with a JSON object in this exact format: {\"category\": \"Category\", \"reasoning\": \"Brief reasoning here\"}. Do NOT include any extra text."
    },
    {
        "role": "user",
        "content": f"Classify the following 911 call into one of these categories: {', '.join(categories)}.\n\nTranscript:\n{transcript_text}"
    }
]

parsed_result = {}
try:
    # API Call to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=150  # Ensure enough space for JSON response
    )

    # Extract GPT response correctly
    result = response.choices[0].message.content.strip()

    # Debugging output
    print("GPT Response:", result)

    # Parse JSON safely
    parsed_result = json.loads(result)

    # Attach keyword info to the parsed result
    parsed_result["keywords_found"] = keywords_found
    parsed_result["high_priority"] = bool(keywords_found)

    print("\nCategorization Result:")
    print(f"Category: {parsed_result['category']}")
    print(f"Reasoning: {parsed_result['reasoning']}")

    # Persist result
    with open(os.path.join(CATEGORIZED_DIR, "call_category.json"), "w") as f:
        json.dump(parsed_result, f, indent=2)

    # If keywords were found, persist a copy into a high‑priority queue
    if keywords_found:
        HIGH_PRIORITY_DIR = os.path.join(STATION_DATA_DIR, "high_priority_queue")
        os.makedirs(HIGH_PRIORITY_DIR, exist_ok=True)
        with open(os.path.join(HIGH_PRIORITY_DIR, "flagged_call.json"), "w") as hp_file:
            json.dump(parsed_result, hp_file, indent=2)

    if keywords_found:
        print(f"\n⚠️  HIGH‑PRIORITY CALL flagged – keywords detected: {keywords_found}")

except json.JSONDecodeError as e:
    print("Failed to decode JSON:", e)
    print("Raw output from API:", result)
    # Save raw result for debugging
    with open(os.path.join(CATEGORIZED_DIR, "call_category.json"), "w") as f:
        f.write(result)

except Exception as e:
    print("An error occurred:", e)
