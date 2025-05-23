import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

# Define absolute project and data paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SCRIPT_PATH = os.path.join(DATA_DIR, "operator_script.json")

load_dotenv()

station_id = os.getenv("STATION_ID", "UnassignedStation")
STATION_DATA_DIR = os.path.join(DATA_DIR, station_id)
TRANSCRIPT_PATH = os.path.join(STATION_DATA_DIR, "transcripts", "diarized_transcript.json")
EVALUATION_OUTPUT_PATH = os.path.join(STATION_DATA_DIR, "operator_evaluation", "evaluation.json")
FLAGGED_LOG_PATH = os.path.join(STATION_DATA_DIR, "operator_evaluation", "flagged_operator_reviews.json")

# Ensure necessary directories exist
os.makedirs(os.path.join(STATION_DATA_DIR, "transcripts"), exist_ok=True)
os.makedirs(os.path.join(STATION_DATA_DIR, "operator_evaluation"), exist_ok=True)

print(f"DEBUG: Loading transcript from {TRANSCRIPT_PATH}")

# Load OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Check if expected operator script exists
if not os.path.exists(SCRIPT_PATH):
    print("⚠️ operator_script.json not found. Creating a default one...")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SCRIPT_PATH, "w") as f:
        json.dump({
            "script": [
                "911, what is your emergency?",
                "Can I have your location?",
                "Is anyone injured?",
                "Help is on the way."
            ]
        }, f, indent=2)
# Load the expected operator script
with open(SCRIPT_PATH, "r") as f:
    expected_script = json.load(f)
print("DEBUG: Expected operator steps:", expected_script.get("script", []))

# Load and debug-print the actual transcript
with open(TRANSCRIPT_PATH, "r") as f:
    transcribed_call = json.load(f)["transcript"]
print("DEBUG: First 200 characters of transcribed_call:", transcribed_call[:200])

# Construct prompt for GPT evaluation
prompt = f"""
Evaluate the following 911 call transcript against the standard operating procedure.

Expected Call Flow:
{json.dumps(expected_script, indent=2)}

Actual Call Transcript:
{transcribed_call}

Respond only in JSON format using the following keys:
- "compliance_score": A number between 0 and 100
- "missing_steps": A list of SOP steps the operator missed
- "feedback": A brief explanation of what the operator did or didn’t do well
"""

try:
    # Make API call to GPT
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    result = response.choices[0].message.content.strip()
    cleaned_result = result.strip("` \n")
    if cleaned_result.startswith("json"):
        cleaned_result = cleaned_result[len("json"):].strip()
    parsed_result = json.loads(cleaned_result)

    print("\nOperator Evaluation Report:")
    print(f"Compliance Score: {parsed_result['compliance_score']}/100")
    print(f"Missing Steps: {parsed_result['missing_steps']}")
    print(f"Feedback: {parsed_result['feedback']}")

    # Store results
    with open(EVALUATION_OUTPUT_PATH, "w") as f:
        json.dump(parsed_result, f, indent=4)

    # Additional logic for compliance flagging
    FLAGGED_THRESHOLD = 50

    if parsed_result["compliance_score"] < FLAGGED_THRESHOLD:
        print("⚠️ Compliance score below threshold. Flagging for review.")
        flagged_entry = {
            "score": parsed_result["compliance_score"],
            "missing_steps": parsed_result["missing_steps"],
            "feedback": parsed_result["feedback"],
            "transcript_excerpt": transcribed_call[:200]
        }
        try:
            if os.path.exists(FLAGGED_LOG_PATH):
                with open(FLAGGED_LOG_PATH, "r") as f:
                    flagged_data = json.load(f)
            else:
                flagged_data = []

            flagged_data.append(flagged_entry)

            with open(FLAGGED_LOG_PATH, "w") as f:
                json.dump(flagged_data, f, indent=2)
        except Exception as e:
            print("Failed to log flagged entry:", e)

except json.JSONDecodeError as e:
    print("Failed to decode JSON:", e)
    print("Raw output from API:", result)

except Exception as e:
    print("An error occurred:", e)
