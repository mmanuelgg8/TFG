import logging
import os
from dotenv import load_dotenv

from scripts.downloader import UrlConstants, Downloader, DataTypeConstants, DataFilterConstants, ImageFormatConstants
from utils import set_logging

from configuration.configuration import Configuration

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    client_id = os.getenv("COPERNICUS_CLIENT_ID")
    client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

    configuration = Configuration()
    EVALSCRIPTS_PATH: str = str(configuration["evalscripts_path"])

    downloader = Downloader(client_id, client_secret)
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
    evalscript_path = os.path.join(EVALSCRIPTS_PATH, "evalscript.js")
    logger.info("Using evalscript: " + evalscript_path)
    with open(evalscript_path, "r") as f:
        evalscript = f.read()

    print(evalscript)
    url = UrlConstants.COPERNICUS_API_PROCESS.value
    payload = downloader.create_payload(bbox, data, ImageFormatConstants.TIFF.value, evalscript)
    downloader.download(url, payload)
