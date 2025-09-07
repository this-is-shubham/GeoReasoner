from fastapi import FastAPI
from typing import Dict, Optional, List
from hazard_features import HAZARD_FEATURE_MAP
from geocode import nominatim_geocode
from phase3_features import get_disaster_features
from schemas import InterpretationRequest, InterpretationResponse, DisasterFeatures

import dotenv, os, json
import google.generativeai as genai


# ----------------------------
# ENV SETUP
# ----------------------------
dotenv.load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in environment.")

genai.configure(api_key=API_KEY)

# ----------------------------
# GEMINI PROMPT
# ----------------------------
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

model = genai.GenerativeModel("gemini-2.5-flash")

def interpret(user_text: str) -> dict:
    response = model.generate_content([SYSTEM_PROMPT, user_text])
    raw = response.text.strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"LLM did not return JSON: {raw[:200]}")
    return json.loads(raw[start:end+1])

# ----------------------------
# FASTAPI APP
# ----------------------------
app = FastAPI(title="Disaster Interpreter API", version="0.5.0")

@app.post("/interpret", response_model=InterpretationResponse)
def interpret_disaster(req: InterpretationRequest):
    # 1️⃣ LLM interpretation
    base = interpret(req.user_text)
    hazard_type = base.get("disaster_type", "unknown")
    location_text = base.get("location_text", "")

    # 2️⃣ Geocode
    geo = {}
    if location_text:
        try:
            geo = nominatim_geocode(location_text)
            if not geo and "," in location_text:
                geo = nominatim_geocode(location_text.split(",")[-1].strip())
        except Exception as e:
            print(f"Geocoding error: {e}")

    if geo.get("pincode"):
        base["pincode"] = geo["pincode"]

    # 3️⃣ Fetch disaster features (GEE + OSM)
    disaster_features_data = {}
    if geo.get("bounding_box"):
        try:
            disaster_features_data = get_disaster_features(
                bbox=geo["bounding_box"],
                hazard_types=[hazard_type],
            )
        except Exception as e:
            print(f"Error fetching disaster features: {e}")

    disaster_features = DisasterFeatures(**disaster_features_data) if disaster_features_data else None

    # 4️⃣ Return enriched response
    return InterpretationResponse(
        **base,
        lat=geo.get("lat"),
        lon=geo.get("lon"),
        bounding_box=geo.get("bounding_box"),
        features_to_fetch=HAZARD_FEATURE_MAP.get(hazard_type, []),
        disaster_features=disaster_features
    )
