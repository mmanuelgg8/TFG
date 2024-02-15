import logging
from datetime import datetime

from dotenv import load_dotenv
from matplotlib.dates import relativedelta
from models.ml_model import Model
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class RandomForestModel(Model):
    def __init__(
        self, name_id: str, date_interval: relativedelta, start_date: datetime, band_names: list, formula: str, kpi: str
    ):
        super().__init__(name_id, date_interval, start_date, band_names, formula, kpi)

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))
        df = self.get_dataframe()
        self.train, self.test = train_test_split(df, test_size=0.2, shuffle=False)
        self.train: list = self.train
        logger.info("Train: \n{}".format(self.train))
        model = RandomForestRegressor(n_estimators=100)
        self.model_fit = model.fit(self.train, self.train[self.kpi])

        logger.info("Training complete.")

    def evaluate(self):
        predictions = self.model_fit.predict(self.test)
        errors = mean_squared_error(self.test[self.kpi], predictions)
        score = self.model_fit.score(self.test, predictions)

        logger.info("Score: {}".format(score))
        logger.info("Mean Squared Error: {}".format(errors))

    def save_model(self):
        pass
