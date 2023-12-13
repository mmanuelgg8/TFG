import logging
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv
from app.utils.logging import set_logging

load_dotenv()

set_logging()

logger = logging.getLogger(__name__)


class Sentinel2Downloader:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self):
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(
            token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            client_secret=self.client_secret,
        )
        return token

    def download(self):
        client = BackendApplicationClient(client_id=self.client_id)
        logger.info("Client created")
        oauth = OAuth2Session(client=client)
        token = self.get_token()
        url = "https://sh.dataspace.copernicus.eu/api/v1/process"
        # Get the path to the directory containing this script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # Assume that evalscripts directory is a sibling of scripts directory
        evalscripts_directory = os.path.join(script_directory, "..", "scripts", "evalscripts")
        evalscript_path = os.path.join(evalscripts_directory, "evalscript.js")
        with open(evalscript_path, "r") as f:
            evalscript = f.read()
        print(evalscript)
        # evalscript = evalscript.replace("\n", "", 1)
        payload = {
            "input": {
                "bounds": {"bbox": [13.822174072265625, 45.85080395917834, 14.55963134765625, 46.29191774991382]},
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {"maxCloudCoverage": 30},
                    }
                ],
            },
            "evalscript": evalscript,
        }
        resp = oauth.post(
            url,
            json=payload,
        )
        logger.info("Save image to file")
        with open("image.png", "wb") as f:
            f.write(resp.content)


client_id = os.getenv("COPERNICUS_CLIENT_ID")
client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

sentinel = Sentinel2Downloader(client_id, client_secret)
sentinel.download()
