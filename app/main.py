import logging
import os

from scripts.downloader import UrlConstants, Downloader, DataTypeConstants
from utils import set_logging

from configuration.configuration import Configuration

set_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    client_id = os.getenv("COPERNICUS_CLIENT_ID")
    client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

    configuration = Configuration()
    EVALSCRIPTS_PATH: str = str(configuration["evalscripts_path"])

    sentinel = Downloader(client_id, client_secret)
    bbox = [13.822174072265625, 45.85080395917834, 14.55963134765625, 46.29191774991382]
    data = [
        {
            "type": DataTypeConstants.SENTINEL2_L2A.value,
            "dataFilter": {"maxCloudCoverage": 30},
        }
    ]
    evalscript_path = os.path.join(EVALSCRIPTS_PATH, "evalscript.js")
    logger.info("Using evalscript: " + evalscript_path)
    with open(evalscript_path, "r") as f:
        evalscript = f.read()

    print(evalscript)
    url = UrlConstants.COPERNICUS_API_PROCESS.value
    payload = sentinel.create_payload(bbox, data, evalscript)
    sentinel.download(url, payload)
