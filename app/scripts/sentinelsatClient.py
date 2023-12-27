# connect to the API
import os
from datetime import date

from dotenv import load_dotenv
from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson

load_dotenv()
user = os.getenv("COPERNICUS_USER")
password = os.getenv("COPERNICUS_PASSWORD")
if user is None or password is None:
    raise Exception("COPERNICUS_USER or COPERNICUS_PASSWORD not set")
# api = SentinelAPI(user, password, "https://apihub.copernicus.eu/apihub")
api = SentinelAPI(None, None, "https://dataspace.copernicus.eu/process")


# search by polygon, time, and SciHub query keywords
# footprint = geojson_to_wkt(read_geojson("map.geojson"))
footprint = "POLYGON((-6.215864855019264 37.162534357525814,-6.111682075391747 37.162534357525814,-6.111682075391747 37.10259292740977,-6.215864855019264 37.10259292740977,-6.215864855019264 37.162534357525814))"
products = api.query(footprint, date=("20151219", date(2015, 12, 29)), platformname="Sentinel-2")

# convert to Pandas DataFrame
products_df = api.to_dataframe(products)

# sort and limit to first 5 sorted products
products_df_sorted = products_df.sort_values(["cloudcoverpercentage", "ingestiondate"], ascending=[True, True])
products_df_sorted = products_df_sorted.head(5)

# download sorted and reduced products
api.download_all(products_df_sorted.index)
