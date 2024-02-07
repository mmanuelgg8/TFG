import logging
import os
from datetime import datetime
from typing import List

from configuration.configuration import Configuration
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from utils import set_logging
from utils.downloader import DataFilterConstants, DataTypeConstants, Downloader, ImageFormatConstants, UrlConstants

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


def download(
    bbox: List[float],
    evalscript: str,
    start_date: datetime,
    end_date: datetime,
    date_interval: relativedelta,
    name_id: str = "image_",
    type: str = DataTypeConstants.SENTINEL2_L2A.value,
    url: str = UrlConstants.COPERNICUS_API_PROCESS.value,
):
    client_id = os.getenv("COPERNICUS_CLIENT_ID")
    client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

    configuration = Configuration()
    EVALSCRIPTS_PATH: str = str(configuration["evalscripts_path"])
    GEOTIFFS_PATH: str = str(configuration["geotiffs_path"])

    downloader = Downloader(client_id, client_secret)

    evalscript_path = os.path.join(EVALSCRIPTS_PATH, evalscript + ".js")
    logger.info("Using evalscript: " + evalscript_path)
    with open(evalscript_path, "r") as f:
        evalscript = f.read()

    print(evalscript)

    for single_date in downloader.daterange(start_date, end_date, step=date_interval):
        date_start = single_date
        date_end = single_date + date_interval
        data = [
            {
                "type": type,
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
        name = name_id + date_start.strftime("%Y-%m-%d") + "_" + date_end.strftime("%Y-%m-%d")
        downloader.download(url, payload, name)
