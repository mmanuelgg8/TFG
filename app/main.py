import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from models.arima import ArimaModel
from models.random_forest import RandomForestModel
from scripts.download import download
from utils import set_logging

set_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Isla Mayor, Sevilla
    min_x, min_y = -6.215864855019264, 37.162534357525814
    max_x, max_y = -6.111682075391747, 37.10259292740977
    bbox = [min_x, min_y, max_x, max_y]
    evalscript = "ndvi"
    start_date = datetime(2017, 1, 1)
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2022, 1, 1)
    date_interval = relativedelta(weeks=1)
    name_id = "islamayor_ndvi_"
    logger.info("Downloading images...")
    # download(bbox, evalscript, start_date, end_date, date_interval, name_id)

    logger.info("Training models...")
    # arima = ArimaModel(date_interval, start_date)
    random_forest = RandomForestModel(date_interval, start_date, ["B04", "B08"], "NDVI")

    # arima.train_model()
    random_forest.train_model()

    # arima.evaluate()
    random_forest.evaluate()
