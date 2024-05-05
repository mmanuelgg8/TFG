import logging
import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from configuration.configuration import Configuration
from scripts.kpis import KPIs, parse_to_constant_kpi
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


def create_dataframe(data, time, kpi_name) -> pd.DataFrame:
    """Create a dataframe from the data"""
    kpi_constant = parse_to_constant_kpi(kpi_name)
    kpi = KPIs(data, axis=(1, 2), kpi=kpi_constant)
    return pd.DataFrame({kpi_constant.value: kpi.get_kpi(), "time": time})


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
        os.makedirs(dir)

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
