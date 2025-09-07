import zipfile
import os

zip_path = "bhuvan_dem_cdnc43e_ellipsoid.zip"
extract_folder = "bhuvan_dem_data"

# Unzip
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(extract_folder)

print(f"✅ Extracted to: {extract_folder}")
print("📂 Files:", os.listdir(extract_folder))
