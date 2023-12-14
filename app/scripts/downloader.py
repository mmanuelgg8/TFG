import logging
from enum import Enum

from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
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


# Let's define an enum for the different data types we can use
class DataTypeConstants(Enum):
    SENTINEL2_L2A = "sentinel-2-l2a"
    SENTINEL2_L1C = "sentinel-2-l1c"
    SENTINEL1 = "sentinel-1"
    DEM = "dem"
    MODIS = "modis"
    LANDSAT8 = "landsat-8"
    LANDSAT7 = "landsat-7"
    LANDSAT5 = "landsat-5"
    LANDSAT4 = "landsat-4"
    ENVISAT_MERIS = "envisat-meris"
    ENVISAT_AATSR = "envisat-aatsr"
    ENVISAT_ASAI = "envisat-asai"
    PROBAV_S1 = "probav-s1"
    PROBAV_S10 = "probav-s10"
    PROBAV_S5 = "probav-s5"
    PROBAV_S1_TOA = "probav-s1-toa"
    PROBAV_S10_TOA = "probav-s10-toa"
    PROBAV_S5_TOA = "probav-s5-toa"
    PROBAV_S1_SR = "probav-s1-sr"
    PROBAV_S10_SR = "probav-s10-sr"
    PROBAV_S5_SR = "probav-s5-sr"
    PROBAV_S1_TOA_SR = "probav-s1-toa-sr"
    PROBAV_S10_TOA_SR = "probav-s10-toa-sr"
    PROBAV_S5_TOA_SR = "probav-s5-toa-sr"
    PROBAV_S1_CLOUDS = "probav-s1-clouds"
    PROBAV_S10_CLOUDS = "probav-s10-clouds"
    PROBAV_S5_CLOUDS = "probav-s5-clouds"
    PROBAV_S1_TOA_CLOUDS = "probav-s1-toa-clouds"
    PROBAV_S10_TOA_CLOUDS = "probav-s10-toa-clouds"
    PROBAV_S5_TOA_CLOUDS = "probav-s5-toa-clouds"
    PROBAV_S1_SR_CLOUDS = "probav-s1-sr-clouds"
    PROBAV_S10_SR_CLOUDS = "probav-s10-sr-clouds"


class UrlConstants(Enum):
    SENTINEL_API_PROCESS = "https://sh.services.sentinel-hub.com/api/v1/process"
    COPERNICUS_API_PROCESS = "https://sh.dataspace.copernicus.eu/api/v1/process"
    COPERNICUS_CATALOG = "https://scihub.copernicus.eu/apihub/search"


class Downloader:
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

    def download(self, url, payload):
        oauth = OAuth2Session(client=self.client)
        token = self.get_token()
        # url = "https://sh.dataspace.copernicus.eu/api/v1/process"
        url = url
        payload = payload
        resp = oauth.post(
            url,
            json=payload,
        )
        logger.info("Save image to file")
        with open(PNGS_PATH + "image.png", "wb") as f:
            f.write(resp.content)