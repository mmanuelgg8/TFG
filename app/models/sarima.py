import logging
from typing import Dict, List

from dotenv import load_dotenv
from matplotlib import pyplot as plt
from pandas import DataFrame
from models.ml_model import Model
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import pmdarima as pm

from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class SarimaModel(Model):

    def __init__(self, df: DataFrame, kpi: slice, model_params: Dict = {}):
        super().__init__(df, kpi)
        self.model_params: Dict = model_params

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))

        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        self.train: List = self.train
        self.test: List = self.test
        m = self.model_params.get("m", 12)
        seasonal = self.model_params.get("seasonal", True)
        stationary = self.model_params.get("stationary", False)
        logger.info(f"Params: m={m}, seasonal={seasonal}")
        self.model_fit: pm.AutoARIMA = pm.auto_arima(
            self.train[self.kpi], seasonal=seasonal, m=m, stationary=stationary
        )

        logger.info("Training complete.")

    def evaluate(self) -> None:
        predict = self.model_fit.predict(n_periods=len(self.test))
        logger.info("Predict: {}".format(predict))
        mse = mean_squared_error(self.test[self.kpi], predict)
        logger.info("Mean Squared Error: {}".format(mse))

    def predict(self, model_name: str) -> None:
        if self.model_fit is None:
            try:
                if self.model_name:
                    self.model_fit = self.load_model(self.model_name)
                if model_name:
                    self.model_fit = self.load_model(model_name)
            except Exception as e:
                logger.error("Error loading model")
                raise e
        self.train, self.test = train_test_split(self.df, test_size=0.3, shuffle=False)
        predict = self.model_fit.predict(n_periods=len(self.test))
        logger.info("Predict: {}".format(predict))

    def save_visualization(self, path: str, name_id: str, interval_type: str) -> None:
        self.train, self.test = train_test_split(self.df, test_size=0.3, shuffle=False)
        plt.plot(self.train[self.kpi], color="blue")
        plt.plot(self.test[self.kpi], color="orange")
        # plt.scatter(npself.test), self.test, color="orange", marker="x")
        logger.info(f"Test: {self.test} - {self.test[self.kpi]} - {self.test.index} and type {type(self.test)}")
        prediction = self.model_fit.predict(n_periods=len(self.test))
        plt.plot(range(len(self.train), len(self.train) + len(self.test)), prediction, color="green")
        future = self.model_fit.predict(n_periods=len(self.df))
        plt.plot(range(len(self.df), len(self.df) + len(future)), future, color="purple")
        predict_in_sample = self.model_fit.predict_in_sample()
        plt.plot(range(len(self.df), len(self.df) + len(predict_in_sample)), predict_in_sample, color="red")
        plt.legend(["Training", "Test", "Prediction", "Future", "Predict in sample"])
        plt.title("SARIMA Model")
        plt.title(f"{name_id} - SARIMA Model")
        plt.xlabel(f"Time ({interval_type})")
        plt.ylabel(f"KPI ({self.kpi})")
        plt.savefig(path)
        plt.close()
        logger.info(f"Visualization saved as {path}")
