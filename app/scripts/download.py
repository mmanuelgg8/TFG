import logging
import os
from datetime import datetime
from typing import List, Optional

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
    format: str = ImageFormatConstants.TIFF.value,
    type: str = DataTypeConstants.SENTINEL2_L2A.value,
    url: str = UrlConstants.COPERNICUS_API_PROCESS.value,
    token_url: str = UrlConstants.COPERNICUS_TOKEN.value,
    data_filter: Optional[dict] = None,
    client_id_env: Optional[str] = "COPERINICUS_CLIENT_ID",
    client_secret_env: Optional[str] = "COPERNICUS_CLIENT_SECRET",
):
    if client_id_env and client_secret_env:
        logger.info(client_id_env)
        logger.info("Using '" + client_id_env + "' and '" + client_secret_env + "' from environment variables")
        client_id: str = str(os.getenv(client_id_env))
        client_secret: str = str(os.getenv(client_secret_env))
    else:
        raise ValueError("client_id_env and client_secret_env are required")

    configuration = Configuration()
    EVALSCRIPTS_PATH: str = str(configuration["evalscripts_path"])

    downloader = Downloader(client_id, client_secret, token_url)

    evalscript_path = os.path.join(EVALSCRIPTS_PATH, evalscript + ".js")
    logger.info("Using evalscript: " + evalscript_path)
    with open(evalscript_path, "r") as f:
        evalscript = f.read()

    print(evalscript)

    for single_date in downloader.daterange(start_date, end_date, step=date_interval):
        date_start: datetime = single_date
        date_end: datetime = single_date + date_interval
        filters = {
            DataFilterConstants.MAX_CLOUD_COVERAGE.value: 30,
            DataFilterConstants.MIN_CLOUD_COVERAGE.value: 0,
            DataFilterConstants.TIME_RANGE.value: {
                DataFilterConstants.FROM.value: date_start.isoformat() + "Z",
                DataFilterConstants.TO.value: date_end.isoformat() + "Z",
            },
        }

        if data_filter:
            filters.update(data_filter)

        data = [{"type": type, "dataFilter": filters}]
        payload = downloader.create_payload(bbox, data, format, evalscript)
        name = date_start.strftime("%Y-%m-%d") + "_" + date_end.strftime("%Y-%m-%d")
        downloader.download(url, payload, name_id, name)
