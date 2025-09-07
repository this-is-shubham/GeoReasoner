# # app.py
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Optional, Dict
# from hazard_features import HAZARD_FEATURE_MAP
# from geocode import nominatim_geocode
# from phase3_features import fetch_disaster_features  # <- integrated OSM fetch

# import dotenv, os, json
# import google.generativeai as genai

# dotenv.load_dotenv()

# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     raise ValueError("Please set GEMINI_API_KEY in environment.")

# genai.configure(api_key=API_KEY)

# # ----------------------------
# # MODELS
# # ----------------------------
# class InterpretationRequest(BaseModel):
#     user_text: str

# class InterpretationResponse(BaseModel):
#     disaster_type: str
#     location_text: str
#     pincode: str
#     time_horizon: str
#     severity_hint: str
#     notes: str
#     confidence: float
#     lat: Optional[float] = None
#     lon: Optional[float] = None
#     bounding_box: Optional[List[List[float]]] = None
#     features_to_fetch: List[str]
#     disaster_features: Optional[Dict] = None  # <- OSM/phase3 features

# # ----------------------------
# # GEMINI PROMPT
# # ----------------------------
# SYSTEM_PROMPT = """
# You are an emergency disaster interpreter for India. 
# The user will give you a short text like "Kerala has gotten flooded" or 
# "Earthquake hit Guwahati yesterday" or "Mumbai is facing a heatwave".

# Your job: Convert it into STRICT JSON with the following keys:

# {
#   "disaster_type": "...",
#   "location_text": "...",
#   "pincode": "...",
#   "time_horizon": "...",
#   "severity_hint": "...",
#   "notes": "...",
#   "confidence": 0.0
# }

# - disaster_type must be one of: flood, cyclone, earthquake, landslide, wildfire,
#   heatwave, drought, industrial_accident, unknown
# - pincode: if the user explicitly mentions or if you can infer a postal PIN code for the area, include it. Otherwise return "".
# - time_horizon examples: "now", "next_24h", "next_72h"
# - severity_hint: only fill this if the user explicitly uses words like "severe", "mild", "massive", "badly". 
#   Do NOT guess severity based only on the disaster type.
# - confidence is a float between 0 and 1
# - Return ONLY the JSON object, no explanation
# """

# model = genai.GenerativeModel("gemini-2.5-flash")

# def interpret(user_text: str) -> dict:
#     response = model.generate_content([SYSTEM_PROMPT, user_text])
#     raw = response.text.strip()
#     start, end = raw.find("{"), raw.rfind("}")
#     if start == -1 or end == -1:
#         raise ValueError(f"LLM did not return JSON: {raw[:200]}")
#     return json.loads(raw[start:end+1])

# # ----------------------------
# # FASTAPI APP
# # ----------------------------
# app = FastAPI(title="Disaster Interpreter API", version="0.3.0")

# @app.post("/interpret", response_model=InterpretationResponse)
# def interpret_disaster(req: InterpretationRequest):
#     # 1️⃣ LLM interpretation
#     base = interpret(req.user_text)
#     hazard_type = base.get("disaster_type", "unknown")
#     location_text = base.get("location_text", "")

#     # 2️⃣ Geocode
#     geo = {}
#     if location_text:
#         try:
#             geo = nominatim_geocode(location_text)
#             if not geo and "," in location_text:
#                 geo = nominatim_geocode(location_text.split(",")[-1].strip())
#         except Exception as e:
#             print(f"Geocoding error: {e}")

#     if geo.get("pincode"):
#         base["pincode"] = geo["pincode"]

#     # 3️⃣ Fetch disaster features from OSM (Phase 3)
#     disaster_features = {}
#     if geo.get("lat") and geo.get("lon"):
#         try:
#             disaster_features = fetch_disaster_features(
#                 lat=geo["lat"],
#                 lon=geo["lon"],
#                 hazard_type=hazard_type
#             )
#         except Exception as e:
#             print(f"Error fetching disaster features: {e}")

#     # 4️⃣ Return enriched response
#     return InterpretationResponse(
#         **base,
#         lat=geo.get("lat"),
#         lon=geo.get("lon"),
#         bounding_box=geo.get("bounding_box"),
#         features_to_fetch=HAZARD_FEATURE_MAP.get(hazard_type, []),
#         disaster_features=disaster_features
#     )

# app.py
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Optional, Dict
# from hazard_features import HAZARD_FEATURE_MAP
# from geocode import nominatim_geocode
# from phase3_features import fetch_disaster_features_bhoonidhi, fetch_disaster_features_osm

# import dotenv, os, json
# import google.generativeai as genai

# dotenv.load_dotenv()

# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     raise ValueError("Please set GEMINI_API_KEY in environment.")

# genai.configure(api_key=API_KEY)

# # ----------------------------
# # MODELS
# # ----------------------------
# class InterpretationRequest(BaseModel):
#     user_text: str

# class InterpretationResponse(BaseModel):
#     disaster_type: str
#     location_text: str
#     pincode: str
#     time_horizon: str
#     severity_hint: str
#     notes: str
#     confidence: float
#     lat: Optional[float] = None
#     lon: Optional[float] = None
#     bounding_box: Optional[List[List[float]]] = None
#     features_to_fetch: List[str]
#     disaster_features: Optional[Dict] = None  # <- OSM + Bhoonidhi

# # ----------------------------
# # GEMINI PROMPT
# # ----------------------------
# SYSTEM_PROMPT = """
# You are an emergency disaster interpreter for India. 
# The user will give you a short text like "Kerala has gotten flooded" or 
# "Earthquake hit Guwahati yesterday" or "Mumbai is facing a heatwave".

# Your job: Convert it into STRICT JSON with the following keys:

# {
#   "disaster_type": "...",
#   "location_text": "...",
#   "pincode": "...",
#   "time_horizon": "...",
#   "severity_hint": "...",
#   "notes": "...",
#   "confidence": 0.0
# }

# - disaster_type must be one of: flood, cyclone, earthquake, landslide, wildfire,
#   heatwave, drought, industrial_accident, unknown
# - pincode: if the user explicitly mentions or if you can infer a postal PIN code for the area, include it. Otherwise return "".
# - time_horizon examples: "now", "next_24h", "next_72h"
# - severity_hint: only fill this if the user explicitly uses words like "severe", "mild", "massive", "badly". 
#   Do NOT guess severity based only on the disaster type.
# - confidence is a float between 0 and 1
# - Return ONLY the JSON object, no explanation
# """

# model = genai.GenerativeModel("gemini-2.5-flash")

# def interpret(user_text: str) -> dict:
#     response = model.generate_content([SYSTEM_PROMPT, user_text])
#     raw = response.text.strip()
#     start, end = raw.find("{"), raw.rfind("}")
#     if start == -1 or end == -1:
#         raise ValueError(f"LLM did not return JSON: {raw[:200]}")
#     return json.loads(raw[start:end+1])

# # ----------------------------
# # FASTAPI APP
# # ----------------------------
# app = FastAPI(title="Disaster Interpreter API", version="0.3.0")

# @app.post("/interpret", response_model=InterpretationResponse)
# def interpret_disaster(req: InterpretationRequest):
#     # 1️⃣ LLM interpretation
#     base = interpret(req.user_text)
#     hazard_type = base.get("disaster_type", "unknown")
#     location_text = base.get("location_text", "")

#     # 2️⃣ Geocode
#     geo = {}
#     if location_text:
#         try:
#             geo = nominatim_geocode(location_text)
#             if not geo and "," in location_text:
#                 geo = nominatim_geocode(location_text.split(",")[-1].strip())
#         except Exception as e:
#             print(f"Geocoding error: {e}")

#     if geo.get("pincode"):
#         base["pincode"] = geo["pincode"]

#     # 3️⃣ Fetch disaster features: Bhoonidhi → fallback to OSM
#     disaster_features = {}
#     if geo.get("lat") and geo.get("lon"):
#         try:
#             disaster_features = fetch_disaster_features_bhoonidhi(
#                 lat=geo["lat"],
#                 lon=geo["lon"],
#                 hazard_type=hazard_type
#             )
#             if not disaster_features:  # fallback if Bhoonidhi empty
#                 print("⚠️ Bhoonidhi returned no data, falling back to OSM...")
#                 disaster_features = fetch_disaster_features_osm(
#                     lat=geo["lat"],
#                     lon=geo["lon"],
#                     hazard_type=hazard_type
#                 )
#         except Exception as e:
#             print(f"Error with Bhoonidhi, falling back to OSM: {e}")
#             try:
#                 disaster_features = fetch_disaster_features_osm(
#                     lat=geo["lat"],
#                     lon=geo["lon"],
#                     hazard_type=hazard_type
#                 )
#             except Exception as e2:
#                 print(f"Error with OSM too: {e2}")

#     # 4️⃣ Return enriched response
#     return InterpretationResponse(
#         **base,
#         lat=geo.get("lat"),
#         lon=geo.get("lon"),
#         bounding_box=geo.get("bounding_box"),
#         features_to_fetch=HAZARD_FEATURE_MAP.get(hazard_type, []),
#         disaster_features=disaster_features
#     )


# app.py
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List, Optional, Dict
# from hazard_features import HAZARD_FEATURE_MAP
# from geocode import nominatim_geocode
# from phase3_features import get_disaster_features  # ✅ use correct function

# import dotenv, os, json
# import google.generativeai as genai

# # ----------------------------
# # ENV SETUP
# # ----------------------------
# dotenv.load_dotenv()

# API_KEY = os.getenv("GEMINI_API_KEY")
# BHOONIDHI_USER = os.getenv("BHOONIDHI_USER")
# BHOONIDHI_PASS = os.getenv("BHOONIDHI_PASS")

# if not API_KEY:
#     raise ValueError("Please set GEMINI_API_KEY in environment.")
# if not BHOONIDHI_USER or not BHOONIDHI_PASS:
#     raise ValueError("Please set BHOONIDHI_USER and BHOONIDHI_PASS in environment.")

# genai.configure(api_key=API_KEY)

# # ----------------------------
# # MODELS
# # ----------------------------
# class InterpretationRequest(BaseModel):
#     user_text: str

# class InterpretationResponse(BaseModel):
#     disaster_type: str
#     location_text: str
#     pincode: str
#     time_horizon: str
#     severity_hint: str
#     notes: str
#     confidence: float
#     lat: Optional[float] = None
#     lon: Optional[float] = None
#     bounding_box: Optional[List[List[float]]] = None
#     features_to_fetch: List[str]
#     disaster_features: Optional[Dict] = None  # ✅ Bhoonidhi + OSM data

# # ----------------------------
# # GEMINI PROMPT
# # ----------------------------
# SYSTEM_PROMPT = """
# You are an emergency disaster interpreter for India. 
# The user will give you a short text like "Kerala has gotten flooded" or 
# "Earthquake hit Guwahati yesterday" or "Mumbai is facing a heatwave".

# Your job: Convert it into STRICT JSON with the following keys:

# {
#   "disaster_type": "...",
#   "location_text": "...",
#   "pincode": "...",
#   "time_horizon": "...",
#   "severity_hint": "...",
#   "notes": "...",
#   "confidence": 0.0
# }

# - disaster_type must be one of: flood, cyclone, earthquake, landslide, wildfire,
#   heatwave, drought, industrial_accident, unknown
# - pincode: if the user explicitly mentions or if you can infer a postal PIN code for the area, include it. Otherwise return "".
# - time_horizon examples: "now", "next_24h", "next_72h"
# - severity_hint: only fill this if the user explicitly uses words like "severe", "mild", "massive", "badly". 
#   Do NOT guess severity based only on the disaster type.
# - confidence is a float between 0 and 1
# - Return ONLY the JSON object, no explanation
# """

# model = genai.GenerativeModel("gemini-2.5-flash")

# def interpret(user_text: str) -> dict:
#     response = model.generate_content([SYSTEM_PROMPT, user_text])
#     raw = response.text.strip()
#     start, end = raw.find("{"), raw.rfind("}")
#     if start == -1 or end == -1:
#         raise ValueError(f"LLM did not return JSON: {raw[:200]}")
#     return json.loads(raw[start:end+1])

# # ----------------------------
# # FASTAPI APP
# # ----------------------------
# app = FastAPI(title="Disaster Interpreter API", version="0.3.0")

# @app.post("/interpret", response_model=InterpretationResponse)
# def interpret_disaster(req: InterpretationRequest):
#     # 1️⃣ LLM interpretation
#     base = interpret(req.user_text)
#     hazard_type = base.get("disaster_type", "unknown")
#     location_text = base.get("location_text", "")

#     # 2️⃣ Geocode
#     geo = {}
#     if location_text:
#         try:
#             geo = nominatim_geocode(location_text)
#             if not geo and "," in location_text:
#                 geo = nominatim_geocode(location_text.split(",")[-1].strip())
#         except Exception as e:
#             print(f"Geocoding error: {e}")

#     if geo.get("pincode"):
#         base["pincode"] = geo["pincode"]

#     # 3️⃣ Fetch disaster features (Bhoonidhi + OSM)
#     disaster_features = {}
#     if geo.get("bounding_box"):
#         try:
#             disaster_features = get_disaster_features(
#                 bbox=geo["bounding_box"],
#                 bhoonidhi_user=BHOONIDHI_USER,
#                 bhoonidhi_pass=BHOONIDHI_PASS,
#                 hazard_type=hazard_type
#             )
#         except Exception as e:
#             print(f"Error fetching disaster features: {e}")

#     # 4️⃣ Return enriched response
#     return InterpretationResponse(
#         **base,
#         lat=geo.get("lat"),
#         lon=geo.get("lon"),
#         bounding_box=geo.get("bounding_box"),
#         features_to_fetch=HAZARD_FEATURE_MAP.get(hazard_type, []),
#         disaster_features=disaster_features
#     )

# from fastapi import FastAPI
# from typing import Dict, Optional, List
# from hazard_features import HAZARD_FEATURE_MAP
# from geocode import nominatim_geocode
# from phase3_features import get_disaster_features  # ✅ pulls OSM + Bhoonidhi
# from schemas import InterpretationRequest, InterpretationResponse

# import dotenv, os, json
# import google.generativeai as genai

# # ----------------------------
# # ENV SETUP
# # ----------------------------
# dotenv.load_dotenv()

# API_KEY = os.getenv("GEMINI_API_KEY")
# BHOONIDHI_USER = os.getenv("BHOONIDHI_USER")
# BHOONIDHI_PASS = os.getenv("BHOONIDHI_PASS")

# if not API_KEY:
#     raise ValueError("Please set GEMINI_API_KEY in environment.")
# if not BHOONIDHI_USER or not BHOONIDHI_PASS:
#     raise ValueError("Please set BHOONIDHI_USER and BHOONIDHI_PASS in environment.")

# genai.configure(api_key=API_KEY)

# # ----------------------------
# # GEMINI PROMPT
# # ----------------------------
# SYSTEM_PROMPT = """
# You are an emergency disaster interpreter for India. 
# The user will give you a short text like "Kerala has gotten flooded" or 
# "Earthquake hit Guwahati yesterday" or "Mumbai is facing a heatwave".

# Your job: Convert it into STRICT JSON with the following keys:

# {
#   "disaster_type": "...",
#   "location_text": "...",
#   "pincode": "...",
#   "time_horizon": "...",
#   "severity_hint": "...",
#   "notes": "...",
#   "confidence": 0.0
# }

# - disaster_type must be one of: flood, cyclone, earthquake, landslide, wildfire,
#   heatwave, drought, industrial_accident, unknown
# - pincode: if the user explicitly mentions or if you can infer a postal PIN code for the area, include it. Otherwise return "".
# - time_horizon examples: "now", "next_24h", "next_72h"
# - severity_hint: only fill this if the user explicitly uses words like "severe", "mild", "massive", "badly". 
#   Do NOT guess severity based only on the disaster type.
# - confidence is a float between 0 and 1
# - Return ONLY the JSON object, no explanation
# """

# model = genai.GenerativeModel("gemini-2.5-flash")

# def interpret(user_text: str) -> dict:
#     response = model.generate_content([SYSTEM_PROMPT, user_text])
#     raw = response.text.strip()
#     start, end = raw.find("{"), raw.rfind("}")
#     if start == -1 or end == -1:
#         raise ValueError(f"LLM did not return JSON: {raw[:200]}")
#     return json.loads(raw[start:end+1])

# # ----------------------------
# # FASTAPI APP
# # ----------------------------
# app = FastAPI(title="Disaster Interpreter API", version="0.3.0")

# @app.post("/interpret", response_model=InterpretationResponse)
# def interpret_disaster(req: InterpretationRequest):
#     # 1️⃣ LLM interpretation
#     base = interpret(req.user_text)
#     hazard_type = base.get("disaster_type", "unknown")
#     location_text = base.get("location_text", "")

#     # 2️⃣ Geocode
#     geo = {}
#     if location_text:
#         try:
#             geo = nominatim_geocode(location_text)
#             if not geo and "," in location_text:
#                 geo = nominatim_geocode(location_text.split(",")[-1].strip())
#         except Exception as e:
#             print(f"Geocoding error: {e}")

#     if geo.get("pincode"):
#         base["pincode"] = geo["pincode"]

#     # 3️⃣ Fetch disaster features (OSM + Bhoonidhi)
#     disaster_features = {}
#     if geo.get("bounding_box"):
#         try:
#             disaster_features = get_disaster_features(
#                 bbox=geo["bounding_box"],
#                 bhoonidhi_user=BHOONIDHI_USER,
#                 bhoonidhi_pass=BHOONIDHI_PASS,
#                 hazard_type=hazard_type
#             )
#         except Exception as e:
#             print(f"Error fetching disaster features: {e}")

#     # 4️⃣ Return enriched response
#     return InterpretationResponse(
#         **base,
#         lat=geo.get("lat"),
#         lon=geo.get("lon"),
#         bounding_box=geo.get("bounding_box"),
#         features_to_fetch=HAZARD_FEATURE_MAP.get(hazard_type, []),
#         disaster_features=disaster_features
#     )

# trial.py
from fastapi import FastAPI
from typing import Dict, Optional, List
from hazard_features import HAZARD_FEATURE_MAP
from geocode import nominatim_geocode
from phase3_features import get_disaster_features  # ✅ pulls OSM + Bhoonidhi
from schemas import InterpretationRequest, InterpretationResponse, DisasterFeatures

import dotenv, os, json
import google.generativeai as genai

# ----------------------------
# ENV SETUP
# ----------------------------
dotenv.load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
BHOONIDHI_USER = os.getenv("BHOONIDHI_USER")
BHOONIDHI_PASS = os.getenv("BHOONIDHI_PASS")

if not API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in environment.")
if not BHOONIDHI_USER or not BHOONIDHI_PASS:
    raise ValueError("Please set BHOONIDHI_USER and BHOONIDHI_PASS in environment.")

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
# HAZARD LAYER MAPPING
# ----------------------------
hazard_layer_map = {
    "flood": ["Flood Hazard Zone"],
    "cyclone": ["Cyclone Risk Zone"],
    "earthquake": ["Earthquake Hazard Zone"],
    "landslide": ["Landslide Hazard Zone"],
    "drought": ["Drought Risk Zone"],
    "wildfire": ["Forest Fire Hazard Zone"],  # If Bhoonidhi supports
    "heatwave": [],  # Bhoonidhi may not support
    "industrial_accident": [],
    "unknown": []
}

# ----------------------------
# FASTAPI APP
# ----------------------------
app = FastAPI(title="Disaster Interpreter API", version="0.3.1")

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

    # 3️⃣ Fetch disaster features (OSM + Bhoonidhi)
    disaster_features_data = {}
    if geo.get("bounding_box"):
        try:
            disaster_features_data = get_disaster_features(
                bbox=geo["bounding_box"],
                bhoonidhi_user=BHOONIDHI_USER,
                bhoonidhi_pass=BHOONIDHI_PASS,
                hazard_types=hazard_layer_map.get(hazard_type, [])
            )
        except Exception as e:
            print(f"Error fetching disaster features: {e}")

    # Wrap in Pydantic model for proper validation + Swagger
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
