# # from pydantic import BaseModel
# # from typing import List, Optional, Tuple

# # class InterpretationRequest(BaseModel):
# #     user_text: str

# # class InterpretationResponse(BaseModel):
# #     disaster_type: str
# #     location_text: str
# #     pincode: Optional[str]
# #     time_horizon: str
# #     severity_hint: str
# #     notes: str
# #     confidence: float
# #     lat: Optional[float]
# #     lon: Optional[float]
# #     bounding_box: Optional[List[Tuple[float, float]]]  # (lat, lon) pairs
# #     features_to_fetch: List[str]

# from pydantic import BaseModel
# from typing import List, Optional, Tuple, Dict

# class InterpretationRequest(BaseModel):
#     user_text: str

# class InterpretationResponse(BaseModel):
#     disaster_type: str
#     location_text: str
#     pincode: Optional[str]
#     time_horizon: str
#     severity_hint: str
#     notes: str
#     confidence: float
#     lat: Optional[float]
#     lon: Optional[float]
#     bounding_box: Optional[List[Tuple[float, float]]]  # (lat, lon) pairs
#     features_to_fetch: List[str]
#     disaster_features: Optional[Dict] = None   # ✅ add this

from pydantic import BaseModel
from typing import List, Optional, Tuple, Dict, Any

# Request model
class InterpretationRequest(BaseModel):
    user_text: str

# OSM feature structure
class OSMFeature(BaseModel):
    lat: Optional[float]
    lon: Optional[float]
    tags: Dict[str, Any]

# Disaster features structure
class DisasterFeatures(BaseModel):
    hazard_data: Dict[str, Any] = {}      # Bhoonidhi layers
    osm_features: Dict[str, List[OSMFeature]] = {}  # OSM points

# Response model
class InterpretationResponse(BaseModel):
    disaster_type: str
    location_text: str
    pincode: Optional[str]
    time_horizon: str
    severity_hint: str
    notes: str
    confidence: float
    lat: Optional[float]
    lon: Optional[float]
    bounding_box: Optional[List[Tuple[float, float]]]  # (lat, lon) pairs
    features_to_fetch: List[str]
    disaster_features: Optional[DisasterFeatures] = None
