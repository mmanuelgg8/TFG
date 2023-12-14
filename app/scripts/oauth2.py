import logging
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv
from utils.logging import set_logging
from configuration.configuration import Configuration

load_dotenv()

set_logging()
logger = logging.getLogger(__name__)

configuration = Configuration()
MBTILES_PATH: str = str(configuration["mbtiles_path"])
GEOTIFFS_PATH: str = str(configuration["geotiffs_path"])
TILES_PATH: str = str(configuration["tiles_path"])
PNGS_PATH: str = str(configuration["pngs_path"])


class Sentinel2Downloader:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = BackendApplicationClient(client_id=self.client_id)
        logger.info("Client created")

    def get_token(self):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(
            token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            client_secret=self.client_secret,
        )
        return token

    def create_payload(self, bbox, data, evalscript):
        payload = {
            "input": {
                "bounds": {"bbox": bbox},
                "data": data,
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{"identifier": "default", "format": {"type": "image/png"}}],
            },
            "evalscript": evalscript,
        }
        return payload

    def download(self, payload):
        oauth = OAuth2Session(client=self.client)
        token = self.get_token()
        url = "https://sh.dataspace.copernicus.eu/api/v1/process"
        payload = payload
        resp = oauth.post(
            url,
            json=payload,
        )
        logger.info("Save image to file")
        with open(PNGS_PATH + "image.png", "wb") as f:
            f.write(resp.content)
