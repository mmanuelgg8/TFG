import logging
from enum import Enum

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from configuration.configuration import Configuration
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
    MAX_DATE = "maxDate"
    MIN_DATE = "minDate"
    TIME = "time"
    GEOMETRY = "geometry"
    MBR = "mbr"
    CRS = "crs"
    GEOMETRY_ID = "geometryId"
    GEOMETRY_IDS = "geometryIds"
    ORBIT_DIRECTION = "orbitDirection"
    PRODUCT_TYPE = "productType"
    SENSOR_OPERATIONAL_MODE = "sensorOperationalMode"
    INGESTION_DATE = "ingestionDate"
    INGESTION_DATE_FROM = "ingestionDateFrom"
    INGESTION_DATE_TO = "ingestionDateTo"
    INGESTION_DATE_BEFORE = "ingestionDateBefore"
    INGESTION_DATE_AFTER = "ingestionDateAfter"
    INGESTION_DATE_DURING = "ingestionDateDuring"
    INGESTION_DATE_RELATIVE = "ingestionDateRelative"
    INGESTION_DATE_RELATIVE_DAYS = "ingestionDateRelativeDays"
    INGESTION_DATE_RELATIVE_WEEKS = "ingestionDateRelativeWeeks"
    INGESTION_DATE_RELATIVE_MONTHS = "ingestionDateRelativeMonths"
    INGESTION_DATE_RELATIVE_YEARS = "ingestionDateRelativeYears"
    INGESTION_DATE_RELATIVE_TO = "ingestionDateRelativeTo"
    INGESTION_DATE_RELATIVE_FROM = "ingestionDateRelativeFrom"
    INGESTION_DATE_RELATIVE_TO_FROM = "ingestionDateRelativeToFrom"
    INGESTION_DATE_RELATIVE_TO_TO = "ingestionDateRelativeToTo"
    INGESTION_DATE_RELATIVE_TO_BEFORE = "ingestionDateRelativeToBefore"
    INGESTION_DATE_RELATIVE_TO_AFTER = "ingestionDateRelativeToAfter"
    INGESTION_DATE_RELATIVE_TO_DURING = "ingestionDateRelativeToDuring"
    INGESTION_DATE_RELATIVE_TO_RELATIVE = "ingestionDateRelativeToRelative"
    INGESTION_DATE_RELATIVE_TO_RELATIVE_DAYS = "ingestionDateRelativeToRelativeDays"
    INGESTION_DATE_RELATIVE_TO_RELATIVE_WEEKS = "ingestionDateRelativeToRelativeWeeks"
    INGESTION_DATE_RELATIVE_TO_RELATIVE_MONTHS = "ingestionDateRelativeToRelativeMonths"
    INGESTION_DATE_RELATIVE_TO_RELATIVE_YEARS = "ingestionDateRelativeToRelativeYears"


class ImageFormatConstants(Enum):
    PNG = "image/png"
    TIFF = "image/tiff"
    JPEG = "image/jpeg"


class Downloader:
    def __init__(self, client_id, client_secret):
        self.client_id: str = client_id
        self.client_secret: str = client_secret

    def get_token(self, oauth):
        token = oauth.fetch_token(
            token_url=UrlConstants.COPERNICUS_TOKEN.value,
            client_secret=self.client_secret,
        )
        return token

    def oauth(self):
        client = BackendApplicationClient(client_id=self.client_id)
        logger.info("Authenticating with client id: " + str(self.client_id))
        oauth = OAuth2Session(client_id=self.client_id, client=client)
        oauth.token = self.get_token(oauth)
        logger.info("Authenticated")
        return oauth

    def create_payload(self, bbox, data, format, evalscript):
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

    def download(self, url, payload):
        oauth = self.oauth()
        logger.info("Using URL: " + url)
        resp = oauth.post(
            url,
            json=payload,
        )
        if resp.status_code != 200:
            logger.error("Error downloading image")
            logger.error(resp.content)
            return
        format = payload["output"]["responses"][0]["format"]["type"]
        if format == ImageFormatConstants.TIFF.value:
            with open(GEOTIFFS_PATH + "image.tif", "wb") as f:
                f.write(resp.content)
        elif format == ImageFormatConstants.PNG.value:
            with open(PNGS_PATH + "image.png", "wb") as f:
                f.write(resp.content)
        logger.info("Image downloaded")
