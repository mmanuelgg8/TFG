import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import rasterio
from dotenv import load_dotenv
from matplotlib.dates import relativedelta
from scripts.kpis import KPIs, KPIsConstants

from configuration.configuration import Configuration
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
        date_interval: relativedelta,
        start_date: datetime,
        band_names: List[str],
        formula: str,
    ):
        tifs, time = self.tifs_to_array(start_date, date_interval)
        bands: List[Dict[str, List[Any]]] = self.extract_bands_from_tifs(band_names, tifs)

        logger.info("Band names: {}".format(band_names))
        logger.info("Bands: {}".format(bands))

        data: np.ndarray = self.get_data(self.parse_formula(formula), bands)

        logger.info("Data shape: {}".format(data.shape))
        logger.info("Data: {}".format(data))

        self.df = pd.DataFrame({"mean": data.mean(axis=0), "time": time})

    def get_dataframe(self) -> pd.DataFrame:
        return self.df

    def create_dataframe(self, data: np.ndarray, time: np.ndarray, kpi_name: str, axis) -> pd.DataFrame:
        kpi = KPIs(data, axis=axis, kpi=KPIsConstants[kpi_name])
        return pd.DataFrame({kpi_name: kpi.get_kpi(), "time": time})

    def parse_formula(self, formula: str) -> str:
        """
        If the formula is a constant, get the value of the constant
        """
        if formula in FormulaConstants.__members__:
            return FormulaConstants[formula].value
        return formula

    def get_data(self, formula: str, bands: List[Dict[str, List[Any]]]) -> np.ndarray:
        """
        Get the data from the bands using the formula
        """
        data = np.array([self.apply_formula(formula, band) for band in bands])
        return np.nan_to_num(data)

    def apply_formula(self, formula: str, bands: Dict[str, List[Any]]):
        """
        Apply the formula to the bands replacing the band names with the actual values
        For example, if the formula is "NDVI = (B08 - B04) / (B08 + B04)", the band names are ["B08", "B04"] and the values are [band8, band4]
        the result is (band8 - band4) / (band8 + band4)
        """

        return eval(formula, bands)

    def extract_bands_from_tifs(self, band_names, tifs) -> List[Dict[str, List[Any]]]:
        """
        Extract the bands from a list of tifs and store them in a list
        """
        bands = []
        for tif in tifs:
            bands.append(self.extract_bands_from_tif(band_names, tif))
        return bands

    def extract_bands_from_tif(self, band_names, tif) -> Dict[str, List[Any]]:
        """
        Extract the bands from a tif and store them in a dictionary
        The dictionary will have the band name as the key and the band as the value
        For example, if the band names are ["B04", "B08"], the dictionary will be {"B04": <band4>, "B08": <band8>}
        """
        bands = {}
        with rasterio.open(tif) as src:
            data = src.read()
            for i, band in enumerate(band_names):
                bands[band] = data[i]
        return bands

    def tifs_to_array(self, start_date, date_interval) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert the tifs to a numpy array and return the array and the time values
        """
        tifs = []
        time_values = []
        current_date = start_date

        for tif in sorted(Path(self.geotiffs_path).iterdir()):
            if not tif.name.endswith(".xml"):
                # Calculate the current date
                current_date += date_interval

                if not tif.name.endswith("-error"):
                    tifs.append(tif)

                    # Add the month number or week number to the time_values list depending on the date_interval
                    if date_interval.months > 0:
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
