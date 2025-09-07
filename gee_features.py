# gee_features.py
import ee
import os

# Authenticate & Initialize GEE
if not ee.data._credentials:
    service_account = os.getenv("GEE_SERVICE_ACCOUNT")
    private_key_file = os.getenv("GEE_KEY_FILE")  # path to service account JSON key
    if service_account and private_key_file:
        credentials = ee.ServiceAccountCredentials(service_account, private_key_file)
        ee.Initialize(credentials)
    else:
        ee.Initialize()

def get_gee_hazard_data(bbox, hazard_types):
    """
    bbox: [[min_lat, min_lon], [max_lat, max_lon]]
    hazard_types: ["flood", "earthquake", "landslide", "drought", ...]
    """
    min_lat, min_lon = bbox[0]
    max_lat, max_lon = bbox[1]
    region = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

    result = {}

    # Flood Risk (JRC Global Surface Water occurrence %)
    if "flood" in hazard_types:
        jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
        flood_mean = jrc.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=region, scale=30, maxPixels=1e9
        ).get("occurrence")
        result["flood_risk_percent"] = flood_mean.getInfo() if flood_mean else None

    # Earthquake Risk (SEDAC GSHAP PGA)
    if "earthquake" in hazard_types:
        gshap = ee.Image("SEDAC/GSHAP/seismic_hazard")
        eq_val = gshap.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=region, scale=10000, maxPixels=1e9
        ).get("PGA")
        result["earthquake_pga"] = eq_val.getInfo() if eq_val else None

    # Landslide Susceptibility (NASA GLSDS)
    if "landslide" in hazard_types:
        landslide = ee.Image("NASA/GLSDS/landslide_susceptibility")
        ls_val = landslide.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=region, scale=1000, maxPixels=1e9
        ).get("susceptibility")
        result["landslide_index"] = ls_val.getInfo() if ls_val else None

    # Drought (CHIRPS Rainfall Anomaly)
    if "drought" in hazard_types:
        rainfall = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterDate("2024-01-01", "2024-12-31") \
            .mean()
        rain_val = rainfall.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=5000,
            maxPixels=1e9
        ).get("precipitation")
        result["avg_rainfall_mm"] = rain_val.getInfo() if rain_val else None

    return result
