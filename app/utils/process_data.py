import logging
import warnings
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


def process_data(
    name_id: str,
    date_interval: relativedelta,
    interval_type: str,
    start_date: datetime,
    band_names: List[str],
    formula: Optional[str],
) -> pd.DataFrame:
    """
    Process the data and return a dataframe
    """

    logger.info("Name ID: {}".format(name_id))
    tifs, time = tifs_to_array(name_id, start_date, date_interval, interval_type)
    bands: List[Dict[str, List[Any]]] = extract_bands_from_tifs(band_names, tifs)

    # logger.info("Bands: {}".format(bands))
    if formula is None:
        data: np.ndarray = np.array(bands)
        data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)
    else:
        data: np.ndarray = get_data(parse_formula(formula), bands)

    logger.info("Data shape: {}".format(data.shape))
    # logger.info("Data: {}".format(data))
    return create_dataframe(data, formula, time)


def create_dataframe(data, time, kpi_name) -> pd.DataFrame:
    """Create a dataframe from the data"""
    kpi_constant = parse_to_constant_kpi(kpi_name)
    kpi = KPIs(data, axis=(1, 2), kpi=kpi_constant)
    return pd.DataFrame({kpi_constant.value: kpi.get_kpi(), "time": time})


def get_data(formula: str, bands: List[Dict[str, Any]]) -> np.ndarray:
    """
    Get the data from the bands using the formula
    """
    data = np.array([apply_formula(formula, band) for band in bands])
    return np.nan_to_num(data, nan=0, posinf=0, neginf=0)


def extract_bands_from_tifs(band_names, tifs) -> List[Dict[str, List[Any]]]:
    """
    Extract the bands from a list of tifs and store them in a list
    """
    bands = []
    for tif in tifs:
        bands.append(extract_bands_from_tif(band_names, tif))
    return bands


def extract_bands_from_tif(band_names, tif) -> Dict[str, List[Any]]:
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


def tifs_to_array(name_id, start_date, date_interval, interval_type) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert the tifs to a numpy array and return the array and the time values
    """
    tifs = []
    time_values = []
    current_date = start_date

    config = Configuration()
    geotiffs_path = str(config["geotiffs_path"])
    # path to geotiffs folder union the name_id
    tifs_dir: Path = Path(geotiffs_path)
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
                if interval_type == "months":
                    time_values.append(current_date.month)
                else:  # Assume weeks if not months
                    time_values.append(current_date.isocalendar()[1])

    tifs = np.array(tifs)
    logger.info("TIFs shape: {}".format(tifs.shape))
    time_values = np.array(time_values)
    logger.info("Time values shape: {}".format(time_values.shape))
    logger.info("Time values: {}".format(time_values))

    return (tifs, time_values)


def parse_formula(formula: str) -> str:
    """
    If the formula is a constant, get the value of the constant
    """
    if formula in FormulaConstants.__members__:
        return FormulaConstants[formula].value
    return formula


def apply_formula(formula: str, bands: Dict[str, List[Any]]):
    """
    Apply the formula to the bands replacing the band names with the actual values
    For example, if the formula is "NDVI = (B08 - B04) / (B08 + B04)", the band names are ["B08", "B04"] and the values are [band8, band4]
    the result is (band8 - band4) / (band8 + band4)
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return eval(formula, bands)
