import logging
import os

import openeo
from dotenv import load_dotenv
from openeo.rest.connection import Connection
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class OpenEOClient:
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        self.client_id = os.getenv("COPERNICUS_CLIENT_ID")
        logger.info("Client id: " + str(self.client_id))
        self.client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")
        self.connection = openeo.connect(url).authenticate_oidc_client_credentials(self.client_id, self.client_secret)
        logger.info("Supported collection ids: " + str(self.connection.list_collection_ids()))

    def connect(self):
        self.connection = openeo.connect(self.url)
        if self.username and self.password:
            self.connection.authenticate_basic(self.username, self.password)

    def list_collections(self):
        return self.connection.list_collections()

    def list_processes(self):
        return self.connection.list_processes()

    def download(self, collection_id, bbox, time_interval, bands, output_path):
        collection = self.connection.load_collection(collection_id)
        datacube = collection.filter_bbox(west=bbox[0], south=bbox[1], east=bbox[2], north=bbox[3], crs="EPSG:4326")
        datacube = datacube.filter_temporal(start_date=time_interval[0], end_date=time_interval[1])
        datacube = datacube.filter_bands(bands=bands)
        result = datacube.download(format="GTiff")
        with open(output_path, "wb") as f:
            f.write(result)
