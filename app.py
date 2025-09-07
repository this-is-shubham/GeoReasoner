# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from hazard_features import HAZARD_FEATURE_MAP
from geocode import nominatim_geocode   # <-- use your existing geocode.py

import dotenv, os, json
import google.generativeai as genai

dotenv.load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in environment.")

genai.configure(api_key=API_KEY)

# ----------------------------
# MODELS
# ----------------------------
class InterpretationRequest(BaseModel):
    user_text: str

class InterpretationResponse(BaseModel):
    disaster_type: str
    location_text: str
    pincode: str
    time_horizon: str
    severity_hint: str
    notes: str
    confidence: float
    lat: Optional[float] = None
    lon: Optional[float] = None
    bounding_box: Optional[List[List[float]]] = None
    features_to_fetch: List[str]

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
app = FastAPI(title="Disaster Interpreter API", version="0.2.0")

@app.post("/interpret", response_model=InterpretationResponse)
def interpret_disaster(req: InterpretationRequest):
    # Step 1: LLM interpretation
    base = interpret(req.user_text)
    hazard_type = base.get("disaster_type", "unknown")
    location_text = base.get("location_text", "")
    pincode = base.get("pincode", "")

    # Step 2: Geocode with fallback
    geo = {}
    try:
        if location_text:
            print(f"[DEBUG] Trying geocode → {location_text}")
            geo = nominatim_geocode(location_text)

        # Fallback 1: broader city (take last part after comma)
        if not geo and "," in location_text:
            broader_query = location_text.split(",")[-1].strip()
            print(f"[DEBUG] Fallback to broader query → {broader_query}")
            geo = nominatim_geocode(broader_query)

        # Fallback 2: pincode-based lookup
        if not geo and pincode:
            pin_query = f"{pincode} India"
            print(f"[DEBUG] Fallback to pincode query → {pin_query}")
            geo = nominatim_geocode(pin_query)

    except Exception as e:
        print(f"[ERROR] Geocoding failed: {e}")

    # Step 3: Prefer geocode pincode if available
    if geo.get("pincode"):
        base["pincode"] = geo["pincode"]

    # Step 4: Return enriched response
    return InterpretationResponse(
        **base,
        lat=geo.get("lat"),
        lon=geo.get("lon"),
        bounding_box=geo.get("bounding_box"),
        features_to_fetch=HAZARD_FEATURE_MAP.get(hazard_type, [])
    )

# Run with: uvicorn app:app --reload
