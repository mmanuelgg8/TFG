import logging
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from models.forecast import TimeSeriesModel
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class ArimaModel(TimeSeriesModel):
    def __init__(self, geotiffs_path: str):
        super().__init__(geotiffs_path)
        self.models: List[ARIMA] = []
        self.models_fit: List[ARIMA] = []
        self.predictions: List[np.ndarray] = []
        self.errors: List[float] = []
        self.error_pixels: List[int] = []

    def train_model(self) -> None:
        tifs = self.tifs_to_array()
        logger.info("Tifs shape: {}".format(tifs.shape))
        tifs = tifs.transpose(2, 3, 1, 0)  # (height, width, bands, time)
        tifs_flat = tifs.reshape((-1, tifs.shape[-1]))  # (height * width * bands, time)
        logger.info("Tifs reshape: {}".format(tifs.shape))
        logger.info("Tifs flat shape: {}".format(tifs_flat.shape))

        # Train ARIMA model for each pixel
        self.error_pixels = []
        for i in range(tifs_flat.shape[0]):
            try:
                model = ARIMA(tifs_flat[i], order=(1, 1, 0))
                model_fit = model.fit()
                self.models.append(model)
                self.models_fit.append(model_fit)
            except Exception as e:
                logger.error(f"Failed to train model for pixel {i}: {e}")
                self.error_pixels.append(i)

    def predict(self):
        logger.info("Predicting {}...".format(self.__class__.__name__))
        self.predictions = []
        for model_fit in self.models_fit:
            start = len(model_fit.data.orig_endog)
            end = len(model_fit.data.orig_endog) + 5
            self.predictions.append(
                model_fit.predict(start=start, end=end, params=model_fit.handle_params, typ="linear")
            )

    def evaluate(self):
        self.errors = []
        for i in range(len(self.predictions)):
            try:
                error = mean_squared_error(self.predictions[i][-5:], self.models_fit[i].data.orig_endog[-5:])
                self.errors.append(float(error))
            except Exception as e:
                logger.error(f"Failed to evaluate model for pixel {i}: {e}")

    def visualize(self):
        # Visualize the predictions
        for i in range(len(self.predictions)):
            plt.plot(self.predictions[i])
            plt.plot(self.models_fit[i].data.orig_endog)
            plt.show()
