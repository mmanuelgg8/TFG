import logging
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from sklearn.metrics import mean_squared_error
from utils import set_logging
from models.forecast import TimeSeriesModel

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class SimpleCNNModel(TimeSeriesModel):
    def __init__(self, geotiffs_path: str):
        super().__init__(geotiffs_path)
        self.predictions: List[np.ndarray] = []
        self.errors: List[float] = []
        self.tifs = self.tifs_to_array()
        self.tifs = self.tifs.transpose(2, 3, 1, 0)  # (height, width, bands, time)
        self.tifs_flat = self.tifs.reshape((-1, self.tifs.shape[-1]))  # (height * width * bands, time)
        self.tifs_train = self.tifs_flat[:, :-1]  # (height * width * bands, time - 1)
        self.tifs_test = self.tifs_flat[:, -1]  # (height * width * bands, 1)
        self.target_variable_for_evaluation = self.tifs_test.flatten()
        self.target_variable_for_visualization = self.tifs_test.reshape((self.tifs.shape[0], self.tifs.shape[1], -1))
        self.model = self.build_model()

    def build_model(self):
        data, _ = self.tifs_train.shape
        model = Sequential()
        model.add(Dense(32, activation="relu", input_shape=(self.tifs_train.shape[1],)))
        model.add(Dense(64, activation="relu"))
        return model

    def train_model(self):
        logger.info("Training {}...".format(self.__class__.__name__))

        data, _ = self.tifs_train.shape

        self.model.compile(optimizer="adam", loss="mse")

        # Train the model
        self.model.fit(self.tifs_train, self.tifs_test, epochs=10, batch_size=32, validation_split=0.2)

        logger.info("Training complete.")

    def predict(self):
        logger.info("Predicting {}...".format(self.__class__.__name__))
        self.predictions = []

        for i in range(self.tifs_test.shape[0]):
            prediction = self.model.predict(self.tifs_test[i].reshape(1, 11))
            self.predictions.append(prediction.flatten())

    def evaluate(self):
        self.errors = []
        for i in range(len(self.predictions)):
            try:
                error = mean_squared_error(self.predictions[i], self.target_variable_for_evaluation[i])
                self.errors.append(float(error))
            except Exception as e:
                logger.error(f"Failed to evaluate model for pixel {i}: {e}")

    def visualize(self):
        # Visualize the predictions
        for i in range(len(self.predictions)):
            plt.plot(self.predictions[i])
            plt.plot(self.target_variable_for_visualization[i])  # Replace with your true values for visualization
            plt.show()
