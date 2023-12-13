import os
import logging
from utils import set_logging
from scripts.oauth2 import Sentinel2Downloader

set_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    client_id = os.getenv("COPERNICUS_CLIENT_ID")
    client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

    sentinel = Sentinel2Downloader(client_id, client_secret)
    sentinel.download()
