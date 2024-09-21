import requests
import os

# Define the STAC and RASTER API endpoints
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

# Define the collection name for the ODIAC dataset
collection_name = "odiac-ffco2-monthgrid-v2023"

# Fetch the collection metadata from the STAC API
collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()

# Print the properties of the collection
print(collection)

# Define the function to count the number of items in the collection
def get_item_count(collection_id):
    count = 0
    items_url = f"{STAC_API_URL}/collections/{collection_id}/items"
    
    while True:
        response = requests.get(items_url)
        if not response.ok:
            print("Error getting items")
            exit()

        stac = response.json()
        count += int(stac["context"].get("returned", 0))
        
        next = [link for link in stac["links"] if link["rel"] == "next"]
        if not next:
            break

        items_url = next[0]["href"]

    return count

# Apply the function to get the total number of items
number_of_items = get_item_count(collection_name)

# Fetch all items (granules) in the collection
items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={number_of_items}").json()["features"]

# Print the total number of items found
print(f"Found {len(items)} items")

# Get the first item (as an example)
first_item = items[0]

# Print the details of the first item
print(first_item)

# Find the GeoTIFF asset in the first item
geotiff_asset = None
for asset_key, asset_value in first_item["assets"].items():
    if asset_value["type"] == "image/tiff":
        geotiff_asset = asset_value["href"]
        break

# Check if a GeoTIFF was found
if geotiff_asset:
    print(f"GeoTIFF found: {geotiff_asset}")
    
    # Define a local file path to save the GeoTIFF
    local_file_path = "odiac_geotiff.tif"
    
    # Download the GeoTIFF
    response = requests.get(geotiff_asset, stream=True)
    
    if response.status_code == 200:
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"GeoTIFF downloaded successfully and saved as {local_file_path}")
    else:
        print("Failed to download the GeoTIFF.")
else:
    print("No GeoTIFF asset found in the first item.")
