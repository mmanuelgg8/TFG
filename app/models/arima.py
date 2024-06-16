import logging
from typing import Dict, List

from dotenv import load_dotenv
from matplotlib import pyplot as plt
from pandas import DataFrame
from models.ml_model import Model
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class ArimaModel(Model):

    def __init__(self, df: DataFrame, kpi: slice, model_params: Dict = {}):
        super().__init__(df, kpi)
        self.model_params: Dict = model_params

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))

        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        self.train: List = self.train
        self.test: List = self.test
        p = self.model_params.get("p", 5)
        d = self.model_params.get("d", 1)
        q = self.model_params.get("q", 0)
        model: ARIMA = ARIMA(self.train[self.kpi], order=(p, d, q))
        self.model_fit: ARIMAResults = model.fit()

        logger.info("Training complete.")

    def evaluate(self) -> None:
        summary = self.model_fit.summary()
        logger.info(f"Summary: {summary}")

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
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        forecast = self.model_fit.forecast(steps=len(self.test))
        logger.info("Forecast: {}".format(forecast))

    def save_visualization(self, path: str, name_id: str, interval_type: str) -> None:
        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        plt.plot(self.train[self.kpi], color="blue")
        plt.plot(self.test[self.kpi], color="orange")
        forecast = self.model_fit.forecast(steps=len(self.test))
        off_set = len(self.train)
        plt.plot(range(off_set, off_set + len(forecast)), forecast, color="green")
        future = self.model_fit.forecast(steps=len(self.df))
        plt.plot(range(len(self.df), len(self.df) + len(future)), future, color="red")
        plt.legend(["Train", "Test", "Forecast", "Future"])
        plt.title("ARIMA Model")
        plt.title(f"{name_id} - ARIMA Model")
        plt.xlabel(f"Time ({interval_type})")
        plt.ylabel(f"KPI ({self.kpi})")
        plt.savefig(path)
        plt.close()
        logger.info(f"Visualization saved as {path}")
