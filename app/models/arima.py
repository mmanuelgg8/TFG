from datetime import datetime
import logging
from matplotlib.dates import relativedelta

from dotenv import load_dotenv
from models.ml_model import Model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class ArimaModel(Model):

    def __init__(self, date_interval: relativedelta, start_date: datetime, band_names: list, formula: str):
        super().__init__(date_interval, start_date, band_names, formula)

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))

        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        logger.info("Train: \n{}".format(self.train))
        self.model: ARIMA = ARIMA(self.train["mean"], order=(5, 1, 0))
        self.model_fit: ARIMAResults = self.model.fit()

        logger.info("Training complete.")

    def evaluate(self):
        self.predictions = self.model_fit.forecast(steps=len(self.test))
        self.errors = mean_squared_error(self.test["mean"], self.predictions)

        logger.info("Mean Squared Error: {}".format(self.errors))
