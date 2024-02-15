import logging
import warnings
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import rasterio
from configuration.configuration import Configuration
from dotenv import load_dotenv
from matplotlib.dates import relativedelta
from scripts.kpis import KPIs, parse_to_constant_kpi
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class FormulaConstants(Enum):
    NDVI = "(B08 - B04) / (B08 + B04)"
    EVI = "2.5 * (B08 - B04) / (B08 + 6 * B04 - 7.5 * B02 + 1)"
    LSWI = "(B08 - B11) / (B08 + B11)"
    NDWI = "(B03 - B08) / (B03 + B08)"
    NDSI = "(B03 - B11) / (B03 + B11)"
    NBR = "(B08 - B12) / (B08 + B12)"
    MNDWI = "(B03 - B08) / (B03 + B08)"


class Model:
    config = Configuration()
    geotiffs_path = str(config["geotiffs_path"])

    def __init__(
        self,
        name_id: str,
        date_interval: relativedelta,
        start_date: datetime,
        band_names: List[str],
        formula: str,
        kpi: str,
    ):
        logger.info("Name ID: {}".format(name_id))
        tifs, time = self.tifs_to_array(name_id, start_date, date_interval)
        bands: List[Dict[str, List[Any]]] = self.extract_bands_from_tifs(band_names, tifs)
        self.kpi = kpi

        # logger.info("Bands: {}".format(bands))

        data: np.ndarray = self.get_data(self.parse_formula(formula), bands)

        logger.info("Data shape: {}".format(data.shape))
        # logger.info("Data: {}".format(data))

        self.df: pd.DataFrame = self.create_dataframe(data, time, kpi, axis=(1, 2))

    def get_dataframe(self) -> pd.DataFrame:
        """Get the dataframe of the model"""
        return self.df

    def create_dataframe(self, data: np.ndarray, time: np.ndarray, kpi_name, axis) -> pd.DataFrame:
        """Create a dataframe from the data"""
        kpi_constant = parse_to_constant_kpi(kpi_name)
        kpi = KPIs(data, axis=axis, kpi=kpi_constant)
        return pd.DataFrame({kpi_constant.value: kpi.get_kpi(), "time": time})

    def parse_formula(self, formula: str) -> str:
        """
        If the formula is a constant, get the value of the constant
        """
        if formula in FormulaConstants.__members__:
            return FormulaConstants[formula].value
        return formula

    def get_data(self, formula: str, bands: List[Dict[str, Any]]) -> np.ndarray:
        """
        Get the data from the bands using the formula
        """
        data = np.array([self.apply_formula(formula, band) for band in bands])
        return np.nan_to_num(data, nan=0, posinf=0, neginf=0)

    def apply_formula(self, formula: str, bands: Dict[str, List[Any]]):
        """
        Apply the formula to the bands replacing the band names with the actual values
        For example, if the formula is "NDVI = (B08 - B04) / (B08 + B04)", the band names are ["B08", "B04"] and the values are [band8, band4]
        the result is (band8 - band4) / (band8 + band4)
        """

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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

    def tifs_to_array(self, name_id, start_date, date_interval) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert the tifs to a numpy array and return the array and the time values
        """
        tifs = []
        time_values = []
        current_date = start_date

        # path to geotiffs folder union the name_id
        tifs_dir: Path = Path(self.geotiffs_path)
        dir: Path = tifs_dir.joinpath(name_id)
        if not dir.exists():
            raise FileNotFoundError(f"Directory {dir} does not exist")

        for tif in sorted(dir.iterdir()):
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

    def save_model(self) -> None: ...

    def load_model(self) -> None: ...
