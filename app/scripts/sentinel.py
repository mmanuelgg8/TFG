from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import logging

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting Sentinel-2 download script")

# Replace these with your Copernicus Open Access Hub credentials
username = ""
password = ""

# Connect to the Copernicus Open Access Hub
api = SentinelAPI(username, password, "https://scihub.copernicus.eu/dhus")

# Define your area of interest using a GeoJSON file or WKT geometry
# Here, we use a bounding box as an example
# You can use geojson_to_wkt(read_geojson('your_geojson_file.json')) if you have a GeoJSON file
area_of_interest = geojson_to_wkt(
    {"type": "Polygon", "coordinates": [[[10.0, 40.0], [10.0, 45.0], [15.0, 45.0], [15.0, 40.0], [10.0, 40.0]]]}
)

# Search for Sentinel-2 products
products = api.query(
    area_of_interest, date=("20220101", "20220131"), platformname="Sentinel-2", cloudcoverpercentage=(0, 30)
)

# Print the found products
print(f"Found {len(products)} Sentinel-2 products")

# Download the first product (you can loop through the products to download multiple)
if products:
    product_id = list(products.keys())[0]
    api.download(product_id)
    print(f"Downloading product {product_id}")
else:
    print("No products found for the given criteria")
