import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import re
load_dotenv()

# Define absolute paths for data directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
TRANSCRIPT_PATH = os.path.join(DATA_DIR, "transcripts", "diarized_transcript.json")
CATEGORIZED_DIR = os.path.join(DATA_DIR, "categorized_calls")
# Ensure directories exist
os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)
os.makedirs(CATEGORIZED_DIR, exist_ok=True)

# Retrieve your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set.")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Load actual transcript
with open(TRANSCRIPT_PATH, "r") as f:
    transcript_data = json.load(f)
raw = transcript_data.get("transcript", "")

# If it's a list of segments, join their 'text' fields
if isinstance(raw, list):
    transcript_text = " ".join(seg.get("text", "") for seg in raw)

# If it's one big string with speaker labels, strip them out
elif isinstance(raw, str):
    transcript_text = re.sub(r"\[.*?\]\s*\(\d+\.\d+s?\s*-\s*\d+\.\d+s?\):\s*", "", raw)

else:
    transcript_text = ""

print("DEBUG: First 200 characters of transcript_text:", transcript_text[:200])

# Define categories
categories = ["Fire", "Medical", "Domestic Abuse", "Homicide", "Kidnapping", "Robbery", "Other"]

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

    print("\nCategorization Result:")
    print(f"Category: {parsed_result['category']}")
    print(f"Reasoning: {parsed_result['reasoning']}")

except json.JSONDecodeError as e:
    print("Failed to decode JSON:", e)
    print("Raw output from API:", result)

except Exception as e:
    print("An error occurred:", e)

with open(os.path.join(CATEGORIZED_DIR, "call_category.json"), "w") as f:
    json.dump(parsed_result, f, indent=2)
