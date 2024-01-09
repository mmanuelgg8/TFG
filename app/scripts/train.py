import logging
from math import sqrt
from pathlib import Path

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
from statsmodels.tsa.stattools import adfuller
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


def tifs_to_array(tifs_path: str) -> np.ndarray:
    tifs = list(Path(tifs_path).glob("*.tif"))
    logger.info("Found {} tifs".format(len(tifs)))
    return np.array([rasterio.open(tif).read() for tif in tifs])


def train_model(tifs_path: str) -> None:
    tifs = tifs_to_array(tifs_path)
    logger.info("Tifs shape: {}".format(tifs.shape))

    # Reshape tifs array into 2D array where each row is a pixel and each column is a month
    tifs = tifs.reshape((tifs.shape[0] * tifs.shape[1] * tifs.shape[2], tifs.shape[3]))
    logger.info("Tifs shape: {}".format(tifs.shape))

    # Assume the last column is the target variable (yield)
    X = tifs[:, :-1]
    # X = X.reshape((X.shape[0], X.shape[1] * X.shape[2]))
    X = X.reshape((X.shape[0], 1, X.shape[1]))
    y = tifs[:, -1]
    logger.info("X shape: {}".format(X.shape))
    logger.info("y shape: {}".format(y.shape))

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    logger.info("X_train shape: {}".format(X_train.shape))
    logger.info("X_test shape: {}".format(X_test.shape))
    logger.info("y_train shape: {}".format(y_train.shape))
    logger.info("y_test shape: {}".format(y_test.shape))

    # Define the LSTM model
    model = Sequential()
    model.add(LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dense(1))
    model.compile(loss="mae", optimizer="adam")

    # Fit the model
    # history = model.fit(X_train, y_train, epochs=50, batch_size=72, verbose="2", shuffle=False)

    # Fit the model with validation data
    history_validation = model.fit(
        X_train, y_train, epochs=50, batch_size=72, validation_data=(X_test, y_test), verbose="0", shuffle=False
    )

    # Plot the training and validation loss
    plt.plot(history_validation.history["loss"], label="train")
    plt.plot(history_validation.history["val_loss"], label="test")
    plt.legend()
    plt.show()
    logger.info("LSTM model fitted")

    # Predict the test set results
    y_pred = model.predict(X_test)

    # Compute the R2 score
    r2 = r2_score(y_test, y_pred)
    logger.info("R2 score: {}".format(r2))


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
