from datetime import datetime
import logging
from pathlib import Path
from typing import Tuple
from matplotlib.dates import relativedelta

import numpy as np
import pandas as pd
from scripts.kpis import KPIs
import rasterio
from configuration.configuration import Configuration
from dotenv import load_dotenv
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class Model:
    config = Configuration()
    geotiffs_path = str(config["geotiffs_path"])

    def __init__(self, geotiffs_path: str, date_interval: relativedelta, start_date: datetime):
        self.geotiffs_path = geotiffs_path
        self.date_interval = date_interval
        self.start_date = start_date
        self.tifs, self.time = self.tifs_to_array()
        self.ndvis = self.tifs[:, 3, :, :]  # (idx, height, width) Getting the NDVI band

    def preprocess_data(self):
        self.ndvis = self.ndvis.transpose(1, 2, 0)  # (height, width, time)
        self.ndvis = self.ndvis.reshape(-1, self.ndvis.shape[-1])  # (height * width, time)
        kpis = KPIs(self.ndvis, axis=0)
        self.mean = kpis.get_mean()
        logger.info("Mean shape: {}".format(self.mean.shape))
        self.feature_matrix = np.column_stack((self.mean, self.time))  # Stack the KPIs and the time values
        columns = ["mean", "time"]
        self.df = pd.DataFrame(self.feature_matrix, columns=columns)

    def tifs_to_array(self) -> Tuple[np.ndarray, np.ndarray]:
        tifs = []
        time_values = []
        current_date = self.start_date

        # Get all the tifs in the geotiffs path and append them to the list.
        # If the name of the file does not end with "-error", append it to the list.
        for tif in sorted(Path(self.geotiffs_path).iterdir()):
            # Calculate the current date
            current_date += self.date_interval

            if not tif.name.endswith("-error"):
                with rasterio.open(tif) as src:
                    tifs.append(src.read())

                # Add the month number or week number to the time_values list depending on the date_interval
                if self.date_interval.months > 0:
                    time_values.append(current_date.month)
                else:  # Assume weeks if not months
                    time_values.append(current_date.isocalendar()[1])

        tifs = np.array(tifs)
        logger.info("TIFs shape: {}".format(tifs.shape))
        time_values = np.array(time_values)
        logger.info("Time values shape: {}".format(time_values.shape))

        return (tifs, time_values)

    def train_model(self) -> None: ...

    def predict(self) -> None: ...

    def evaluate(self) -> None: ...

    def visualize(self) -> None: ...

    def save(self) -> None: ...

    def load(self) -> None: ...
