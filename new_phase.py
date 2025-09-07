import requests

# ----------------------------
# BHOONIDHI INTEGRATION
# ----------------------------
def authenticate_bhoonidhi(user_id: str, password: str) -> str:
    """Authenticate and get Bhoonidhi API token"""
    url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi-api/auth/token"
    payload = {"userId": user_id, "password": password}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json().get("access_token")


def fetch_hazard_data(bbox: list, token: str, hazard_type: str) -> dict:
    """
    Fetch hazard data from Bhoonidhi for a bounding box.
    hazard_type must match Bhoonidhi product names like:
      - "Flood Hazard Zone"
      - "Earthquake Hazard Zone"
      - "Cyclone Risk Zone"
      - "Landslide Hazard Zone"
      - "Drought Risk Zone"
    """
    url = "https://bhoonidhi.nrsc.gov.in/bhoonidhi-api/data"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "bbox": ",".join(map(str, [bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1]])),
        "product": hazard_type,
        "format": "json"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


# ----------------------------
# OSM FEATURES FETCHER
# ----------------------------
def fetch_osm_features(bbox: list, feature_types: list) -> dict:
    """Fetch features like hospitals, shelters, roads, critical infra from OSM"""
    OVERPASS_URL = "http://overpass-api.de/api/interpreter"
    feature_map = {
        "hospitals": 'node["amenity"="hospital"]',
        "shelters": 'node["amenity"="shelter"]',
        "roads": 'way["highway"]',
        "critical_infra": 'node["amenity"~"fire_station|police|power|water_works"]'
    }

    features = {}
    min_lat, min_lon = bbox[0]
    max_lat, max_lon = bbox[1]

    for f in feature_types:
        if f not in feature_map:
            continue

        query = f"""
        [out:json][timeout:25];
        (
          {feature_map[f]}({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out center;
        """
        try:
            r = requests.post(OVERPASS_URL, data=query, headers={"User-Agent": "DisasterAI/1.0"})
            r.raise_for_status()
            data = r.json()
            features[f] = [
                {"lat": elem.get("lat", elem.get("center", {}).get("lat")),
                 "lon": elem.get("lon", elem.get("center", {}).get("lon"))}
                for elem in data.get("elements", [])
                if "lat" in elem or "center" in elem
            ]
        except Exception as e:
            print(f"Error fetching {f} from OSM: {e}")
            features[f] = []

    return features


# ----------------------------
# COMBINED FUNCTION
# ----------------------------
def get_disaster_features(
    bbox: list,
    bhoonidhi_user: str,
    bhoonidhi_pass: str,
    hazard_types: list = None
) -> dict:
    """
    Return combined Bhoonidhi + OSM data for disaster analysis.

    hazard_types: list of hazard layers to fetch, e.g.
                  ["Flood Hazard Zone", "Earthquake Hazard Zone", "Cyclone Risk Zone"]
    """
    token = authenticate_bhoonidhi(bhoonidhi_user, bhoonidhi_pass)

    if not hazard_types:
        hazard_types = ["Flood Hazard Zone"]  # default

    hazard_data = {}
    for h in hazard_types:
        try:
            hazard_data[h] = fetch_hazard_data(bbox, token, h)
        except Exception as e:
            print(f"Error fetching {h}: {e}")
            hazard_data[h] = {}

    osm_features = fetch_osm_features(
        bbox,
        ["hospitals", "shelters", "roads", "critical_infra"]
    )

    return {
        "hazard_data": hazard_data,
        "osm_features": osm_features
    }
