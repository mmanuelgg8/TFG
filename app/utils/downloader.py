import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generator

from configuration.configuration import Configuration
from dateutil.relativedelta import relativedelta
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from utils.logging import set_logging

set_logging()
logger = logging.getLogger(__name__)

configuration = Configuration()
MBTILES_PATH: str = str(configuration["mbtiles_path"])
GEOTIFFS_PATH: str = str(configuration["geotiffs_path"])
TILES_PATH: str = str(configuration["tiles_path"])
PNGS_PATH: str = str(configuration["pngs_path"])


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
    COPERNICUS_TOKEN = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


class DataFilterConstants(Enum):
    MAX_CLOUD_COVERAGE = "maxCloudCoverage"
    MIN_CLOUD_COVERAGE = "minCloudCoverage"
    TIME_RANGE = "timeRange"
    FROM = "from"
    TO = "to"
    GEOMETRY = "geometry"
    MBR = "mbr"
    CRS = "crs"
    PRODUCT_TYPE = "productType"
    SENSOR_OPERATIONAL_MODE = "sensorOperationalMode"


class ImageFormatConstants(Enum):
    PNG = "image/png"
    TIFF = "image/tiff"
    JPEG = "image/jpeg"


class Downloader:
    def __init__(self, client_id, client_secret):
        self.client_id: str = client_id
        self.client_secret: str = client_secret

    def get_token(self, oauth, token_url: str = UrlConstants.COPERNICUS_TOKEN.value) -> Dict[str, Any]:
        token = oauth.fetch_token(
            token_url=token_url,
            client_secret=self.client_secret,
        )
        return token

    def oauth(self) -> OAuth2Session:
        try:
            client = BackendApplicationClient(client_id=self.client_id)
            oauth = OAuth2Session(client_id=self.client_id, client=client)
            oauth.token = self.get_token(oauth)
        except Exception as e:
            logger.error("Error getting token for user id " + self.client_id)
            raise e
        return oauth

    def create_payload(self, bbox, data, format, evalscript) -> Dict[str, Any]:
        payload = {
            "input": {
                "bounds": {"bbox": bbox},
                "data": data,
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{"identifier": "default", "format": {"type": format}}],
            },
            "evalscript": evalscript,
        }
        return payload

    def download(self, url: str, payload: Dict[str, Any], image_name: str) -> None:
        oauth = self.oauth()
        resp = oauth.post(
            url,
            json=payload,
        )
        if resp.status_code != 200:
            logger.error("Error downloading image from " + url)
            logger.error(resp.content)
            return
        format = payload["output"]["responses"][0]["format"]["type"]
        image_path = ""
        if format == ImageFormatConstants.TIFF.value:
            image_path = GEOTIFFS_PATH + image_name + ".tif"
        elif format == ImageFormatConstants.PNG.value:
            image_path = PNGS_PATH + image_name + ".png"
        elif format == ImageFormatConstants.JPEG.value:
            image_path = PNGS_PATH + image_name + ".jpg"
        with open(image_path, "wb") as f:
            f.write(resp.content)
        logger.info(f"Image {image_path} downloaded")

    # def daterange(self, start_date: datetime, end_date: datetime, step: int = 1):
    #     for n in range(int((end_date - start_date).days / step)):
    #         yield start_date + timedelta(n * step)

    def daterange(
        self, start_date: datetime, end_date: datetime, step: relativedelta = relativedelta(days=1)
    ) -> Generator[datetime, None, None]:
        current_date = start_date
        while current_date < end_date:
            yield current_date
            current_date += step
