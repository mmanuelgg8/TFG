from datetime import datetime
from enum import Enum
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple
from matplotlib.dates import relativedelta

import numpy as np
import pandas as pd
import rasterio
from configuration.configuration import Configuration
from dotenv import load_dotenv
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class FormulaConstants(Enum):
    NDVI = "(B08 - B04) / (B08 + B04)"
    NDWI = "(B03 - B08) / (B03 + B08)"
    NDBI = "(B11 - B08) / (B11 + B08)"
    EVI = "2.5 * ((B08 - B04) / (B08 + 6 * B04 - 7.5 * B02 + 1))"
    SAVI = "((B08 - B04) / (B08 + B04 + 0.5)) * (1 + 0.5)"
    ARVI = "(B08 - (2 * B04 - B02)) / (B08 + (2 * B04 - B02))"


class Model:
    config = Configuration()
    geotiffs_path = str(config["geotiffs_path"])

    def __init__(
        self,
        geotiffs_path: str,
        date_interval: relativedelta,
        start_date: datetime,
        band_names: List[str],
        formula: str,
    ):
        self.geotiffs_path = geotiffs_path
        self.date_interval = date_interval
        self.start_date = start_date
        tifs, time = self.tifs_to_array()  # Time is an array with the month number or week number of the tif
        bands: List[Dict[str, List[Any]]] = self.extract_bands_from_tifs(band_names, tifs)
        logger.info("Band names: {}".format(band_names))

        if formula in FormulaConstants.__members__:
            self.formula = FormulaConstants[formula].value
        else:
            self.formula = formula

        logger.info("Bands: {}".format(bands))
        logger.info("Band B04: {}".format(bands[0]["B04"]))
        data: np.ndarray = np.array([self.apply_formula(self.formula, band) for band in bands])
        # Clean Nan values
        data = np.nan_to_num(data)
        logger.info("Data shape: {}".format(data.shape))
        logger.info("Data: {}".format(data))
        self.df = pd.DataFrame({"mean": data.mean(axis=0), "time": time})

    def apply_formula(self, formula: str, bands: Dict[str, List[Any]]):
        """
        Apply the formula to the bands replacing the band names with the actual values
        For example, if the formula is "NDVI = (B08 - B04) / (B08 + B04)", the band names are ["B08", "B04"] and the values are [band8, band4]
        the result is (band8 - band4) / (band8 + band4)
        """

        return eval(formula, bands)

    def extract_bands_from_tifs(self, band_names, tifs) -> List[Dict[str, List[Any]]]:
        # Extract the bands from the tifs and store them in a list
        # The bands are stored in a dictionary with the band name as the key and the band as the value
        # For example, if the band names are ["B04", "B08"], the dictionary will be {"B04": <band4>, "B08": <band8>}
        bands = []
        for tif in tifs:
            bands.append(self.extract_bands_from_tif(band_names, tif))
        return bands

    def extract_bands_from_tif(self, band_names, tif) -> Dict[str, List[Any]]:
        # Extract the bands from the tifs and store them in a list
        # The bands are stored in a dictionary with the band name as the key and the band as the value
        # For example, if the band names are ["B04", "B08"], the dictionary will be {"B04": <band4>, "B08": <band8>}
        bands = {}
        with rasterio.open(tif) as src:
            data = src.read()
            for i, band in enumerate(band_names):
                bands[band] = data[i]
        return bands

    def preprocess_data(self):
        # Get a dataframe with the KPIs (mean, as an example) of the evaluated formulas and the time each kpi
        # Example: dataframe = pd.DataFrame({"NDVI": [0.5, 0.6, 0.7], "time": [1, 2, 3]})
        # The dataframe will have the KPIs of the evaluated formulas and the time each kpi
        pass

    def tifs_to_array(self) -> Tuple[np.ndarray, np.ndarray]:
        tifs = []
        time_values = []
        current_date = self.start_date

        # Get all the tifs in the geotiffs path and append them to the list.
        # If the name of the file does not end with "-error", append it to the list.
        for tif in sorted(Path(self.geotiffs_path).iterdir()):
            if not tif.name.endswith(".xml"):
                # Calculate the current date
                current_date += self.date_interval

                if not tif.name.endswith("-error"):
                    tifs.append(tif)

                    # Add the month number or week number to the time_values list depending on the date_interval
                    if self.date_interval.months > 0:
                        time_values.append(current_date.month)
                    else:  # Assume weeks if not months
                        time_values.append(current_date.isocalendar()[1])

        tifs = np.array(tifs)
        logger.info("TIFs shape: {}".format(tifs.shape))
        time_values = np.array(time_values)
        logger.info("Time values shape: {}".format(time_values.shape))
        logger.info("Time values: {}".format(time_values))

        return (tifs, time_values)

    def train_model(self) -> None: ...

    def predict(self) -> None: ...

    def evaluate(self) -> None: ...

    def visualize(self) -> None: ...

    def save(self) -> None: ...

    def load(self) -> None: ...
