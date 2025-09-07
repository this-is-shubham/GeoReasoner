import requests

def nominatim_geocode(location: str) -> dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1, "addressdetails": 1}
    r = requests.get(url, params=params, headers={"User-Agent": "DisasterAI/1.0"})
    r.raise_for_status()
    data = r.json()
    if not data:
        return {}
    item = data[0]
    return {
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "bounding_box": [
            (float(item["boundingbox"][0]), float(item["boundingbox"][2])),
            (float(item["boundingbox"][1]), float(item["boundingbox"][3]))
        ],
        "pincode": item["address"].get("postcode", "")
    }

