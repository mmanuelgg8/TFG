import logging
import os
from datetime import datetime, timedelta

from configuration.configuration import Configuration
from dotenv import load_dotenv
from scripts.downloader import DataFilterConstants, DataTypeConstants, Downloader, ImageFormatConstants, UrlConstants
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
    date_interval = timedelta(days=30)

    # Isla Mayor, Sevilla
    min_x, min_y = -6.215864855019264, 37.162534357525814
    max_x, max_y = -6.111682075391747, 37.10259292740977
    bbox = [min_x, min_y, max_x, max_y]

    evalscript_path = os.path.join(EVALSCRIPTS_PATH, "evalscript.js")
    logger.info("Using evalscript: " + evalscript_path)
    with open(evalscript_path, "r") as f:
        evalscript = f.read()

    print(evalscript)
    url = UrlConstants.COPERNICUS_API_PROCESS.value

    for single_date in downloader.daterange(start_date, end_date, step=30):
        date_start = single_date
        date_end = single_date + date_interval
        data = [
            {
                "type": DataTypeConstants.SENTINEL2_L2A.value,
                "dataFilter": {
                    DataFilterConstants.MAX_CLOUD_COVERAGE.value: 30,
                    DataFilterConstants.MIN_CLOUD_COVERAGE.value: 0,
                    DataFilterConstants.TIME_RANGE.value: {
                        DataFilterConstants.FROM.value: date_start.isoformat() + "Z",
                        DataFilterConstants.TO.value: date_end.isoformat() + "Z",
                    },
                },
            }
        ]
        payload = downloader.create_payload(bbox, data, ImageFormatConstants.TIFF.value, evalscript)
        name = "image_" + date_start.strftime("%Y-%m-%d") + "_" + date_end.strftime("%Y-%m-%d")
        downloader.download(url, payload, name)
