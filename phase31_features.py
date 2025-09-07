# import requests

# OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# def fetch_osm_data(lat, lon, radius_km=5):
#     """
#     Fetch disaster-relevant features from OpenStreetMap within radius_km of lat/lon.
#     Returns structured JSON with multiple categories.
#     """
#     radius = radius_km * 1000  # convert to meters

#     queries = {
#         "hospitals": f"""
#             node(around:{radius},{lat},{lon})["amenity"="hospital"];
#             out center;
#         """,
#         "clinics": f"""
#             node(around:{radius},{lat},{lon})["amenity"~"clinic|doctors"];
#             out center;
#         """,
#         "pharmacies": f"""
#             node(around:{radius},{lat},{lon})["amenity"="pharmacy"];
#             out center;
#         """,
#         "police_stations": f"""
#             node(around:{radius},{lat},{lon})["amenity"="police"];
#             out center;
#         """,
#         "fire_stations": f"""
#             node(around:{radius},{lat},{lon})["amenity"="fire_station"];
#             out center;
#         """,
#         "government_offices": f"""
#             node(around:{radius},{lat},{lon})["office"="government"];
#             out center;
#         """,
#         "shelters": f"""
#             node(around:{radius},{lat},{lon})["amenity"="shelter"];
#             out center;
#         """,
#         "community_centers": f"""
#             node(around:{radius},{lat},{lon})["amenity"="community_centre"];
#             out center;
#         """,
#         "schools": f"""
#             node(around:{radius},{lat},{lon})["amenity"="school"];
#             out center;
#         """,
#         "universities": f"""
#             node(around:{radius},{lat},{lon})["amenity"="university"];
#             out center;
#         """,
#         "roads": f"""
#             way(around:{radius},{lat},{lon})["highway"];
#             out center;
#         """,
#         "railway_stations": f"""
#             node(around:{radius},{lat},{lon})["railway"="station"];
#             out center;
#         """,
#         "bus_stations": f"""
#             node(around:{radius},{lat},{lon})["amenity"="bus_station"];
#             out center;
#         """,
#         "airports": f"""
#             node(around:{radius},{lat},{lon})["aeroway"="aerodrome"];
#             out center;
#         """,
#         "power_substations": f"""
#             node(around:{radius},{lat},{lon})["power"="substation"];
#             out center;
#         """,
#         "fuel_stations": f"""
#             node(around:{radius},{lat},{lon})["amenity"="fuel"];
#             out center;
#         """,
#         "water_towers": f"""
#             node(around:{radius},{lat},{lon})["man_made"="water_tower"];
#             out center;
#         """,
#         "dams": f"""
#             way(around:{radius},{lat},{lon})["man_made"="dam"];
#             out center;
#         """,
#         "bridges": f"""
#             way(around:{radius},{lat},{lon})["man_made"="bridge"];
#             out center;
#         """
#     }

#     results = {}

#     for category, query in queries.items():
#         try:
#             response = requests.post(OVERPASS_URL, data={"data": f"[out:json];{query}"})
#             response.raise_for_status()
#             data = response.json()
#             results[category] = data.get("elements", [])
#         except Exception as e:
#             results[category] = {"error": str(e)}

#     return results

# file: phase3_features.py
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
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OSM_QUERIES = {
    "hospitals": 'node["amenity"="hospital"]',
    "clinics": 'node["amenity"~"clinic|doctors"]',
    "pharmacies": 'node["amenity"="pharmacy"]',
    "police_stations": 'node["amenity"="police"]',
    "fire_stations": 'node["amenity"="fire_station"]',
    "government_offices": 'node["office"="government"]',
    "shelters": 'node["amenity"="shelter"]',
    "community_centers": 'node["amenity"="community_centre"]',
    "schools": 'node["amenity"="school"]',
    "universities": 'node["amenity"="university"]',
    "roads": 'way["highway"]',
    "railway_stations": 'node["railway"="station"]',
    "bus_stations": 'node["amenity"="bus_station"]',
    "airports": 'node["aeroway"="aerodrome"]',
    "power_substations": 'node["power"="substation"]',
    "fuel_stations": 'node["amenity"="fuel"]',
    "water_towers": 'node["man_made"="water_tower"]',
    "dams": 'way["man_made"="dam"]',
    "bridges": 'way["man_made"="bridge"]'
}

def fetch_osm_features(bbox: list, feature_types: list = None) -> dict:
    """Fetch OSM features inside bounding box"""
    if feature_types is None:
        feature_types = list(OSM_QUERIES.keys())

    min_lat, min_lon = bbox[0]
    max_lat, max_lon = bbox[1]

    features = {}
    for f in feature_types:
        query = f"""
        [out:json][timeout:25];
        (
          {OSM_QUERIES[f]}({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out center;
        """
        try:
            r = requests.post(OVERPASS_URL, data=query, headers={"User-Agent": "DisasterAI/1.0"})
            r.raise_for_status()
            data = r.json()
            features[f] = [
                {
                    "lat": elem.get("lat", elem.get("center", {}).get("lat")),
                    "lon": elem.get("lon", elem.get("center", {}).get("lon")),
                    "tags": elem.get("tags", {})
                }
                for elem in data.get("elements", [])
                if "lat" in elem or "center" in elem
            ]
        except Exception as e:
            print(f"Error fetching {f} from OSM: {e}")
            features[f] = []

    return features


# ----------------------------
# COMBINED FUNCTION (Bhoonidhi + OSM with fallback)
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
                  ["Flood Hazard Zone", "Earthquake Hazard Zone"]
    """
    result = {"hazard_data": {}, "osm_features": {}}

    # 1️⃣ Bhoonidhi
    try:
        token = authenticate_bhoonidhi(bhoonidhi_user, bhoonidhi_pass)
        if not hazard_types:
            hazard_types = ["Flood Hazard Zone"]

        for h in hazard_types:
            try:
                result["hazard_data"][h] = fetch_hazard_data(bbox, token, h)
            except Exception as e:
                print(f"Error fetching {h} from Bhoonidhi: {e}")
                result["hazard_data"][h] = {}
    except Exception as e:
        print(f"Skipping Bhoonidhi (auth/data failed): {e}")

    # 2️⃣ OSM fallback (always fetch)
    try:
        result["osm_features"] = fetch_osm_features(bbox)
    except Exception as e:
        print(f"Error fetching OSM features: {e}")
        result["osm_features"] = {}

    return result

