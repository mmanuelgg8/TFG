import logging
from datetime import datetime

from dotenv import load_dotenv
from matplotlib.dates import relativedelta
from models.ml_model import Model
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class ArimaModel(Model):

    def __init__(
        self, name_id: str, date_interval: relativedelta, start_date: datetime, band_names: list, formula: str, kpi: str
    ):
        super().__init__(name_id, date_interval, start_date, band_names, formula, kpi)

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))

        self.train, self.test = train_test_split(self.df, test_size=0.2, shuffle=False)
        logger.info("Train: \n{}".format(self.train))
        model: ARIMA = ARIMA(self.train[self.kpi], order=(5, 1, 0))
        self.model_fit: ARIMAResults = model.fit()

        logger.info("Training complete.")

    def evaluate(self):
        predictions = self.model_fit.forecast(steps=len(self.test))
        errors = mean_squared_error(self.test[self.kpi], predictions)

        logger.info("Mean Squared Error: {}".format(errors))
