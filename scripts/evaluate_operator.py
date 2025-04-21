import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Path to the diarized transcript JSON
TRANSCRIPT_PATH = os.path.join("data", "transcripts", "diarized_transcript.json")
print(f"DEBUG: Loading transcript from {TRANSCRIPT_PATH}")

# Load OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Check if expected operator script exists
if not os.path.exists("data/operator_script.json"):
    print("⚠️ operator_script.json not found. Creating a default one...")
    os.makedirs("data", exist_ok=True)
    with open("data/operator_script.json", "w") as f:
        json.dump({
            "script": [
                "911, what is your emergency?",
                "Can I have your location?",
                "Is anyone injured?",
                "Help is on the way."
            ]
        }, f, indent=2)
# Load the expected operator script
with open("data/operator_script.json", "r") as f:
    expected_script = json.load(f)
print("DEBUG: Expected operator steps:", expected_script.get("script", []))

# Ensure the transcripts directory exists
os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)

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

Provide a JSON response with a compliance score (0-100), a list of missing steps, and feedback on how well the operator followed the script. 

Respond in JSON format:
{{
    "compliance_score": 90,
    "missing_steps": ["nature_of_emergency"],
    "feedback": "The operator did not ask for the nature of the emergency."
}}
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
    with open("data/operator_evaluation.json", "w") as f:
        json.dump(parsed_result, f, indent=4)

except json.JSONDecodeError as e:
    print("Failed to decode JSON:", e)
    print("Raw output from API:", result)

except Exception as e:
    print("An error occurred:", e)
