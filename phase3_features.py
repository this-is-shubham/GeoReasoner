# import requests
# import ee
# import numpy as np

# # Initialize Earth Engine (make sure you authenticated once locally with `ee.Authenticate()`)
# try:
#     #ee.Initialize()
#     ee.Initialize(project='LTI')
# except Exception as e:
#     ee.Authenticate()
#     #ee.Initialize()

    


# # ----------------------------
# # GEE HAZARD ANALYSIS
# # ----------------------------
# def get_flood_extent(bbox):
#     """Return flooded area (km²) using Sentinel-1 water detection"""
#     region = ee.Geometry.Rectangle([bbox[0][1], bbox[0][0], bbox[1][1], bbox[1][0]])
#     s1 = (
#         ee.ImageCollection("COPERNICUS/S1_GRD")
#         .filterBounds(region)
#         .filterDate("2025-01-01", "2025-09-01")  # adjust as needed
#         .filter(ee.Filter.eq("instrumentMode", "IW"))
#         .select("VV")
#     )
#     img = s1.median()
#     water = img.lt(-17)  # VV threshold for water
#     area = water.multiply(ee.Image.pixelArea()).reduceRegion(
#         reducer=ee.Reducer.sum(),
#         geometry=region,
#         scale=30,
#         maxPixels=1e12
#     )
#     return float(area.get("VV").getInfo() or 0) / 1e6  # km²


# def get_rainfall_anomaly(bbox):
#     """Return rainfall anomaly (%) using CHIRPS dataset"""
#     region = ee.Geometry.Rectangle([bbox[0][1], bbox[0][0], bbox[1][1], bbox[1][0]])

#     chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterBounds(region)

#     recent = chirps.filterDate("2025-06-01", "2025-09-01").sum()
#     baseline = chirps.filterDate("2000-06-01", "2020-09-01").mean()

#     anomaly = recent.subtract(baseline).divide(baseline).multiply(100)
#     val = anomaly.reduceRegion(
#         reducer=ee.Reducer.mean(),
#         geometry=region,
#         scale=5000,
#         maxPixels=1e12
#     )
#     return float(val.get("precipitation").getInfo() or 0)


# def get_slope_risk(bbox):
#     """Return % area with slope >30° (landslide proxy) using SRTM DEM"""
#     region = ee.Geometry.Rectangle([bbox[0][1], bbox[0][0], bbox[1][1], bbox[1][0]])
#     dem = ee.Image("USGS/SRTMGL1_003")
#     slope = ee.Terrain.slope(dem)
#     risky = slope.gt(30)

#     area_total = ee.Image.pixelArea().reduceRegion(
#         reducer=ee.Reducer.sum(), geometry=region, scale=90, maxPixels=1e12
#     )
#     area_risky = risky.multiply(ee.Image.pixelArea()).reduceRegion(
#         reducer=ee.Reducer.sum(), geometry=region, scale=90, maxPixels=1e12
#     )

#     total = float(area_total.get("area").getInfo() or 1)
#     risky_area = float(area_risky.get("slope").getInfo() or 0)
#     return (risky_area / total) * 100


# def get_earthquake_zone(lat, lon):
#     """Rough classification using GSHAP seismic hazard zones"""
#     # (GEE dataset placeholder, can refine later)
#     if lat < 25 and lon > 80:
#         return "Moderate Risk"
#     elif lat > 25 and lon > 85:
#         return "High Risk"
#     else:
#         return "Low Risk"


# # ----------------------------
# # OSM FEATURES FETCHER
# # ----------------------------
# OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# OSM_QUERIES = {
#     "hospitals": 'node["amenity"="hospital"]',
#     "shelters": 'node["amenity"="shelter"]',
#     "roads": 'way["highway"]',
#     "critical_infra": 'node["amenity"~"fire_station|police|power|water_works"]'
# }

# def fetch_osm_features(bbox: list, feature_types: list = None) -> dict:
#     """Fetch OSM features inside bounding box"""
#     if feature_types is None:
#         feature_types = list(OSM_QUERIES.keys())

#     min_lat, min_lon = bbox[0]
#     max_lat, max_lon = bbox[1]

#     features = {}
#     for f in feature_types:
#         query = f"""
#         [out:json][timeout:25];
#         (
#           {OSM_QUERIES[f]}({min_lat},{min_lon},{max_lat},{max_lon});
#         );
#         out center;
#         """
#         try:
#             r = requests.post(OVERPASS_URL, data=query, headers={"User-Agent": "DisasterAI/1.0"})
#             r.raise_for_status()
#             data = r.json()
#             features[f] = [
#                 {
#                     "lat": elem.get("lat", elem.get("center", {}).get("lat")),
#                     "lon": elem.get("lon", elem.get("center", {}).get("lon")),
#                     "tags": elem.get("tags", {})
#                 }
#                 for elem in data.get("elements", [])
#                 if "lat" in elem or "center" in elem
#             ]
#         except Exception as e:
#             print(f"Error fetching {f} from OSM: {e}")
#             features[f] = []

#     return features


# # ----------------------------
# # COMBINED FETCHER (GEE + OSM)
# # ----------------------------
# from gee_features import get_gee_hazard_data
# from hazard_features import fetch_osm_features

# def get_disaster_features(
#     bbox: list,
#     hazard_types: list = None
# ) -> dict:
#     """
#     Return combined hazard indicators from GEE + OSM features.
#     """
#     result = {"hazard_data": {}, "osm_features": {}}

#     # GEE hazard indicators
#     try:
#         if hazard_types:
#             result["hazard_data"] = get_gee_hazard_data(bbox, hazard_types)
#     except Exception as e:
#         print(f"GEE hazard fetch failed: {e}")
#         result["hazard_data"] = {}

#     # OSM features
#     try:
#         result["osm_features"] = fetch_osm_features(bbox)
#     except Exception as e:
#         print(f"Error fetching OSM features: {e}")
#         result["osm_features"] = {}

#     return result

# phase3_features.py
import requests
import ee
import numpy as np

# ----------------------------
# Earth Engine Initialization
# ----------------------------
try:
    ee.Initialize(project='My First Project')
except Exception:
    ee.Authenticate()
    #ee.Initialize()

    # try:
#     #ee.Initialize()
#     ee.Initialize(project='LTI')
# except Exception as e:
#     ee.Authenticate()
#     #ee.Initialize()

# ----------------------------
# GEE HAZARD ANALYSIS
# ----------------------------
def get_flood_extent(bbox):
    """Return flooded area (km²) using Sentinel-1 water detection"""
    region = ee.Geometry.Rectangle([bbox[0][1], bbox[0][0], bbox[1][1], bbox[1][0]])
    s1 = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(region)
        .filterDate("2025-01-01", "2025-09-01")  # adjust as needed
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .select("VV")
    )
    img = s1.median()
    water = img.lt(-17)  # VV threshold for water
    area = water.multiply(ee.Image.pixelArea()).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=30,
        maxPixels=1e12
    )
    return float(area.get("VV").getInfo() or 0) / 1e6  # km²


def get_rainfall_anomaly(bbox):
    """Return rainfall anomaly (%) using CHIRPS dataset"""
    region = ee.Geometry.Rectangle([bbox[0][1], bbox[0][0], bbox[1][1], bbox[1][0]])

    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterBounds(region)

    recent = chirps.filterDate("2025-06-01", "2025-09-01").sum()
    baseline = chirps.filterDate("2000-06-01", "2020-09-01").mean()

    anomaly = recent.subtract(baseline).divide(baseline).multiply(100)
    val = anomaly.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=5000,
        maxPixels=1e12
    )
    return float(val.get("precipitation").getInfo() or 0)


def get_slope_risk(bbox):
    """Return % area with slope >30° (landslide proxy) using SRTM DEM"""
    region = ee.Geometry.Rectangle([bbox[0][1], bbox[0][0], bbox[1][1], bbox[1][0]])
    dem = ee.Image("USGS/SRTMGL1_003")
    slope = ee.Terrain.slope(dem)
    risky = slope.gt(30)

    area_total = ee.Image.pixelArea().reduceRegion(
        reducer=ee.Reducer.sum(), geometry=region, scale=90, maxPixels=1e12
    )
    area_risky = risky.multiply(ee.Image.pixelArea()).reduceRegion(
        reducer=ee.Reducer.sum(), geometry=region, scale=90, maxPixels=1e12
    )

    total = float(area_total.get("area").getInfo() or 1)
    risky_area = float(area_risky.get("slope").getInfo() or 0)
    return (risky_area / total) * 100


def get_earthquake_zone(lat, lon):
    """Rough classification using GSHAP seismic hazard zones"""
    if lat < 25 and lon > 80:
        return "Moderate Risk"
    elif lat > 25 and lon > 85:
        return "High Risk"
    else:
        return "Low Risk"

# ----------------------------
# OSM FEATURES FETCHER
# ----------------------------
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OSM_QUERIES = {
    "hospitals": 'node["amenity"="hospital"]',
    "shelters": 'node["amenity"="shelter"]',
    "roads": 'way["highway"]',
    "critical_infra": 'node["amenity"~"fire_station|police|power|water_works"]'
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
# COMBINED FETCHER (GEE + OSM)
# ----------------------------
def get_disaster_features(
    bbox: list,
    hazard_types: list = None
) -> dict:
    """
    Return combined hazard indicators from GEE + OSM features.
    """
    result = {"hazard_data": {}, "osm_features": {}}

    # GEE hazard indicators
    try:
        if hazard_types:
            if "flood" in hazard_types:
                result["hazard_data"]["flooded_area_km2"] = get_flood_extent(bbox)
            if "drought" in hazard_types:
                result["hazard_data"]["rainfall_anomaly"] = get_rainfall_anomaly(bbox)
            if "landslide" in hazard_types:
                result["hazard_data"]["slope_risk_percent"] = get_slope_risk(bbox)
            if "earthquake" in hazard_types:
                lat = (bbox[0][0] + bbox[1][0]) / 2
                lon = (bbox[0][1] + bbox[1][1]) / 2
                result["hazard_data"]["earthquake_risk_zone"] = get_earthquake_zone(lat, lon)
    except Exception as e:
        print(f"GEE hazard fetch failed: {e}")
        result["hazard_data"] = {}

    # OSM features
    try:
        result["osm_features"] = fetch_osm_features(bbox)
    except Exception as e:
        print(f"Error fetching OSM features: {e}")
        result["osm_features"] = {}

    return result


