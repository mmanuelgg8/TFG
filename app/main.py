import logging
import os
from datetime import datetime, timedelta

from configuration.configuration import Configuration
from dotenv import load_dotenv
from scripts.downloader import DataFilterConstants, DataTypeConstants, Downloader, ImageFormatConstants, UrlConstants
from scripts.openeoClient import OpenEOClient
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    client_id = os.getenv("COPERNICUS_CLIENT_ID")
    client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")
    client_user = os.getenv("COPERNICUS_CLIENT_USER")
    client_password = os.getenv("COPERNICUS_CLIENT_PASSWORD")

    configuration = Configuration()
    EVALSCRIPTS_PATH: str = str(configuration["evalscripts_path"])

    downloader = Downloader(client_id, client_secret)
    # Define time range
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2019, 1, 1)
    date_interval = timedelta(weeks=1)  # Daily interval

    # Create a list of data requests for each day in the time range
    data_requests = []
    current_date = start_date
    while current_date <= end_date:
        data_request = {
            "type": DataTypeConstants.SENTINEL2_L2A.value,
            "dataFilter": {
                DataFilterConstants.MAX_CLOUD_COVERAGE.value: 30,
                DataFilterConstants.MIN_CLOUD_COVERAGE.value: 0,
                DataFilterConstants.MIN_DATE.value: current_date.strftime("%Y-%m-%d"),
                DataFilterConstants.MAX_DATE.value: (current_date + date_interval).strftime("%Y-%m-%d"),
            },
        }
        data_requests.append(data_request)
        current_date += date_interval
    # Isla Mayor, Sevilla
    min_x, min_y = -6.215864855019264, 37.162534357525814
    max_x, max_y = -6.111682075391747, 37.10259292740977
    bbox = [min_x, min_y, max_x, max_y]
    data = [
        {
            "type": DataTypeConstants.SENTINEL2_L2A.value,
            "dataFilter": {
                DataFilterConstants.MAX_CLOUD_COVERAGE.value: 30,
                DataFilterConstants.MIN_CLOUD_COVERAGE.value: 0,
                DataFilterConstants.MAX_DATE.value: "2020-01-01",
                DataFilterConstants.MIN_DATE.value: "2019-01-01",
            },
        }
    ]
    # data = data_requests
    evalscript_path = os.path.join(EVALSCRIPTS_PATH, "evalscript.js")
    logger.info("Using evalscript: " + evalscript_path)
    with open(evalscript_path, "r") as f:
        evalscript = f.read()

    print(evalscript)
    url = UrlConstants.COPERNICUS_API_PROCESS.value
    payload = downloader.create_payload(bbox, data, ImageFormatConstants.TIFF.value, evalscript)
    downloader.download(url, payload)

    # # OpenEO
    # openeo_client = OpenEOClient("https://openeo.dataspace.copernicus.eu/openeo/1.2", client_user, client_password)
    # download = openeo_client.download("SENTINEL2_L2A", bbox, ("2019-01-01", "2020-01-01"), ["B04", "B08"], "output.tif")
