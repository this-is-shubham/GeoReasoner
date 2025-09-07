import requests

# 🔑 Replace this with your actual key
API_KEY = "26c59d58dc5c6304f4e44b2822e34988daab99c3"

# Example AOI id (this may need to change based on the dataset you want)
AOI_ID = "cdnc43e"   # from docs
DATUM = "ellipsoid"  # or "geoid"
SE = "CDEM"          # as per docs

url = (
    f"https://bhuvan-app1.nrsc.gov.in/api/geoid/curl_gdal_api.php"
    f"?id={AOI_ID}&datum={DATUM}&se={SE}&key={API_KEY}"
)

print(f"🔗 Requesting: {url}")

try:
    r = requests.get(url, timeout=60)
    r.raise_for_status()

    # Save file
    filename = f"bhuvan_dem_{AOI_ID}_{DATUM}.zip"
    with open(filename, "wb") as f:
        f.write(r.content)

    print(f"✅ DEM downloaded successfully → {filename} ({len(r.content)} bytes)")

except Exception as e:
    print(f"❌ Error: {e}")
    if 'r' in locals():
        print("Response:", r.text[:500])  # print first 500 chars if available
