import logging
from pathlib import Path
from typing import List

import numpy as np
import rasterio
from configuration.configuration import Configuration
from dotenv import load_dotenv
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class TimeSeriesModel:
    config = Configuration()
    geotiffs_path = str(config["geotiffs_path"])

    def __init__(self, geotiffs_path: str):
        self.geotiffs_path = geotiffs_path

    def tifs_to_array(self) -> np.ndarray:
        tifs = list(Path(self.geotiffs_path).glob("*.tif"))
        logger.info("Found {} tifs".format(len(tifs)))
        return np.array([rasterio.open(tif).read() for tif in tifs])

    def train_model(self) -> None:
        pass

    def predict(self) -> None:
        pass

    def evaluate(self) -> None:
        pass

    def visualize(self) -> None:
        pass

    def save(self) -> None:
        pass

    def load(self) -> None:
        pass
