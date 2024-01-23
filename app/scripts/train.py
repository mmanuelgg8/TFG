import logging
from math import sqrt
from pathlib import Path
from typing import List

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from dotenv import load_dotenv
from keras.layers import LSTM, Dense, Dropout
from keras.models import Sequential
from PIL import Image
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


def tifs_to_array(tifs_path: str) -> np.ndarray:
    tifs = list(Path(tifs_path).glob("*.tif"))
    logger.info("Found {} tifs".format(len(tifs)))
    return np.array([rasterio.open(tif).read() for tif in tifs])


def train_arima(tifs_path: str) -> List[ARIMA]:
    tifs = tifs_to_array(tifs_path)
    logger.info("Tifs shape: {}".format(tifs.shape))
    tifs = tifs.transpose(2, 3, 1, 0)  # (height, width, bands, time)
    tifs_flat = tifs.reshape((-1, tifs.shape[-1]))  # (height * width * bands, time)
    logger.info("Tifs reshape: {}".format(tifs.shape))
    logger.info("Tifs flat shape: {}".format(tifs_flat.shape))

    # Train ARIMA model for each pixel
    models = []
    for i in range(tifs_flat.shape[0]):
        model = ARIMA(tifs_flat[i], order=(1, 1, 0))
        model_fit = model.fit()
        models.append(model_fit)

    return models


def train_sarima(tifs_path: str) -> List[SARIMAX]:
    tifs = tifs_to_array(tifs_path)
    logger.info("Tifs shape: {}".format(tifs.shape))
    tifs = tifs.transpose(2, 3, 1, 0)  # (height, width, bands, time)
    tifs_flat = tifs.reshape((-1, tifs.shape[-1]))  # (height * width * bands, time)
    logger.info("Tifs reshape: {}".format(tifs.shape))
    logger.info("Tifs flat shape: {}".format(tifs_flat.shape))

    # Train SARIMA model for each pixel
    models = []
    for i in range(tifs_flat.shape[0]):
        model = SARIMAX(tifs_flat[i], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        model_fit = model.fit()
        models.append(model_fit)

    return models


def calculate_accuracy(forecast_image, true_tifs_path) -> None:
    # Load the true NDVI image for the next month
    true_tifs = tifs_to_array(true_tifs_path)
    true_image = true_tifs.reshape((true_tifs.shape[0], true_tifs.shape[1] * true_tifs.shape[2]))

    # Calculate error metrics
    mae = mean_absolute_error(true_image, forecast_image)
    mse = mean_squared_error(true_image, forecast_image)
    rmse = sqrt(mse)
    logger.info("MAE: {}".format(mae))
    logger.info("MSE: {}".format(mse))
    logger.info("RMSE: {}".format(rmse))
