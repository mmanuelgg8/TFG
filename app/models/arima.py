import logging
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from models.forecast import Model
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class ArimaModel(Model):
    def __init__(self, geotiffs_path: str):
        super().__init__(geotiffs_path)
        self.models: List[ARIMA] = []
        self.models_fit: List[ARIMA] = []
        self.predictions: List[np.ndarray] = []
        self.errors: List[float] = []
        self.error_pixels: List[int] = []
        self.tifs = self.tifs_to_array()
        logger.info("Tifs reshape: {}".format(self.tifs.shape))
        #  Transpose to (height, width, bands, time) and reshape as (height * width * bands, time)
        self.tifs_flat = self.tifs.transpose(2, 3, 1, 0).reshape((-1, self.tifs.shape[-1]))
        logger.info("Tifs flat shape: {}".format(self.tifs_flat.shape))
        self.tifs_train = self.tifs_flat[:-5]
        self.tifs_test = self.tifs_flat[-5:]

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))

        # Train ARIMA model for each pixel
        self.error_pixels = []
        print_interval = 1000
        for i in range(self.tifs_train.shape[0]):
            try:
                model = ARIMA(self.tifs_train[i], order=(1, 1, 0))
                model_fit = model.fit()
                self.models.append(model)
                self.models_fit.append(model_fit)
            except Exception as e:
                logger.error(f"Failed to train model for pixel {i}: {e}")
                self.error_pixels.append(i)

            # Print progress every print_interval iterations
            if (i + 1) % print_interval == 0 or i == self.tifs_train.shape[0] - 1:
                progress_percentage = (i + 1) / self.tifs_train.shape[0] * 100
                logger.info(
                    "Training model {}/{} {:.2f}% done".format(i + 1, self.tifs_train.shape[0], progress_percentage)
                )

        logger.info("Training complete.")

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
                error = mean_squared_error(self.predictions[i], self.tifs_test[i])
                self.errors.append(float(error))
            except Exception as e:
                logger.error(f"Failed to evaluate model for pixel {i}: {e}")

    def visualize(self):
        # Visualize the predictions
        for i in range(len(self.predictions)):
            plt.plot(self.tifs_test[i], label="True Values")
            plt.plot(self.predictions[i], label="Predictions")
            plt.legend()
            plt.show()
