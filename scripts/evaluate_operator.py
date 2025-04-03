import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Load OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Load the expected operator script
with open("data/operator_script.json", "r") as f:
    expected_script = json.load(f)

# Load actual diarized transcript
with open("data/transcripts/diarized_transcript.json") as f:
    transcribed_call = json.load(f)["transcript"]

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
    parsed_result = json.loads(result)

    print("\nOperator Evaluation Report:")
    print(f"Compliance Score: {parsed_result['compliance_score']}/100")
    print(f"Missing Steps: {parsed_result['missing_steps']}")
    print(f"Feedback: {parsed_result['feedback']}")

    # Store results
    with open("data/operator_evaluation.json", "w") as f:
        json.dump(json.loads(response.choices[0].message.content), f, indent=2)

except json.JSONDecodeError as e:
    print("Failed to decode JSON:", e)
    print("Raw output from API:", result)

except Exception as e:
    print("An error occurred:", e)
