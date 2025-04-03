import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Retrieve your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set.")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Example transcript (Replace this with actual transcriptions)
transcript_text = """
Operator: 911, what's your emergency?
Caller: Help, my house is on fire! I can't get out!
"""

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

with open("data/categorized_calls/call_category.json", "w") as f:
    json.dump(json.loads(response.choices[0].message.content), f, indent=2)
