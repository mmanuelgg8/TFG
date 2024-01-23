import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import rasterio
from configuration.configuration import Configuration
from dateutil.relativedelta import relativedelta
from models.arima import ArimaModel
from scripts.download import download
from utils import set_logging

set_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    config = Configuration()
    geotiffs_path = str(config["geotiffs_path"])
    # Isla Mayor, Sevilla
    min_x, min_y = -6.215864855019264, 37.162534357525814
    max_x, max_y = -6.111682075391747, 37.10259292740977
    bbox = [min_x, min_y, max_x, max_y]
    evalscript = "ndvi"
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2019, 1, 1)
    date_interval = relativedelta(months=1)
    name_id = "islamayor_ndvi_"
    logger.info("Downloading images...")
    # download(bbox, evalscript, start_date, end_date, date_interval, name_id)
    # Lets visualize the downloaded images as an array
    tifs = list(Path(geotiffs_path).glob("*.tif"))
    logger.info("Found {} tifs".format(len(tifs)))
    tifs = np.array([rasterio.open(tif).read() for tif in tifs])
    logger.info("Tifs shape: {}".format(tifs.shape))

    logger.info("Training models...")
    arima = ArimaModel(geotiffs_path)
    arima.train_model()
    arima.predict()
    arima.evaluate()
    arima.visualize()
