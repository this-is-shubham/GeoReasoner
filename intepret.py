# now we'll use google gemini to parse the user input and extract relevant information
import dotenv
dotenv.load_dotenv()
import json
import os
import google.generativeai as genai

# Get your key from Google AI Studio and set in env
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in environment.")

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
You are an emergency disaster interpreter for India. 
The user will give you a short text like "Kerala has gotten flooded" or 
"Earthquake hit Guwahati yesterday" or "Mumbai is facing a heatwave".

Your job: Convert it into STRICT JSON with the following keys:

{
  "disaster_type": "...",
  "location_text": "...",
  "pincode": "...",
  "time_horizon": "...",
  "severity_hint": "...",
  "notes": "...",
  "confidence": 0.0
}

- disaster_type must be one of: flood, cyclone, earthquake, landslide, wildfire,
  heatwave, drought, industrial_accident, unknown
- pincode: if the user explicitly mentions or if you can infer a postal PIN code for the area, include it. Otherwise return "".
- time_horizon examples: "now", "next_24h", "next_72h"
- severity_hint: only fill this if the user explicitly uses words like "severe", "mild", "massive", "badly". 
  Do NOT guess severity based only on the disaster type.
- confidence is a float between 0 and 1
- Return ONLY the JSON object, no explanation
"""



model = genai.GenerativeModel("gemini-2.5-flash")  # or gemini-1.5-pro for better quality

def interpret(user_text: str) -> dict:
    response = model.generate_content([SYSTEM_PROMPT, user_text])
    raw = response.text.strip()
    # Extract JSON from response
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"LLM did not return JSON: {raw[:200]}")
    return json.loads(raw[start:end+1])

if __name__ == "__main__":
    user_query=input("Enter a disaster query: ")
    print(interpret(user_query))
