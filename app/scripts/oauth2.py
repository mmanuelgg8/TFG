import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import logging
import os
from dotenv import load_dotenv
from app.logger_setup import setup_logger

load_dotenv()

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger = setup_logger()


client_id = os.getenv("COPERNICUS_CLIENT_ID")
logger.info("Client ID: %s", client_id)
client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

logger.info("Starting Sentinel-2 download script")
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)

token = oauth.fetch_token(
    token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    client_secret=client_secret,
)

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
