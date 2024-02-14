import logging
from datetime import datetime

from dotenv import load_dotenv
from matplotlib.dates import relativedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from models.ml_model import Model
from utils import set_logging

load_dotenv()
set_logging()
logger = logging.getLogger(__name__)


class RandomForestModel(Model):
    def __init__(self, date_interval: relativedelta, start_date: datetime, band_names: list, formula: str):
        super().__init__(date_interval, start_date, band_names, formula)

    def train_model(self) -> None:
        logger.info("Training {}...".format(self.__class__.__name__))
        df = self.get_dataframe()
        # Train the model on the mean over time
        self.train, self.test = train_test_split(df, test_size=0.2, shuffle=False)
        logger.info("Train: \n{}".format(self.train))
        self.model = RandomForestRegressor(n_estimators=100)
        self.model.fit(self.train, self.train["mean"])

        logger.info("Training complete.")

    def evaluate(self):
        self.predictions = self.model.predict(self.test)
        self.errors = mean_squared_error(self.test["mean"], self.predictions)

        logger.info("Mean Squared Error: {}".format(self.errors))
